# Kubernetes Deployment Guide

This guide covers deploying OrionAI to Kubernetes clusters.

## Prerequisites

- Kubernetes 1.24+
- kubectl configured and authenticated
- Helm 3.x (optional, for Helm deployment)
- metrics-server installed (required for HPA)
- Ingress controller (optional, for external access)

## Verify Prerequisites

```bash
# Check kubectl
kubectl version --client

# Check cluster access
kubectl cluster-info

# Check metrics-server
kubectl top nodes

# Check Helm (if using)
helm version
```

## Deployment Options

### Option 1: Raw Kubernetes Manifests

**Deploy everything:**
```bash
kubectl apply -f k8s/
```

**Deploy step-by-step:**
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/pdb.yaml
kubectl apply -f k8s/ingress.yaml
```

### Option 2: Helm Chart

**Install:**
```bash
helm install orionai ./helm/orionai \
  --namespace orionai \
  --create-namespace
```

**Install with custom values:**
```bash
helm install orionai ./helm/orionai \
  --namespace orionai \
  --create-namespace \
  --set image.tag=1.0.0 \
  --set secrets.openaiApiKey="sk-..." \
  --set autoscaling.maxReplicas=20
```

**Install with values file:**
```bash
helm install orionai ./helm/orionai \
  --namespace orionai \
  --create-namespace \
  -f values-prod.yaml
```

## Configuration

### Update Secrets

**Before deploying, update secrets:**

```bash
# Edit k8s/secret.yaml
kubectl create secret generic orionai-secret \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=API_KEY="your-secure-key" \
  --namespace orionai \
  --dry-run=client -o yaml | kubectl apply -f -
```

**For Helm:**
```bash
helm upgrade orionai ./helm/orionai \
  --namespace orionai \
  --set secrets.openaiApiKey="sk-..." \
  --set secrets.apiKey="your-secure-key"
```

### Update ConfigMap

**Edit configuration:**
```bash
kubectl edit configmap orionai-config -n orionai
```

**Or update and reapply:**
```bash
# Edit k8s/configmap.yaml
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment orionai -n orionai
```

### Update Ingress

**Edit ingress host:**
```bash
# Edit k8s/ingress.yaml - change orionai.example.com to your domain
kubectl apply -f k8s/ingress.yaml
```

## Verification

### Check Deployment Status

```bash
# All resources
kubectl get all -n orionai

# Pods
kubectl get pods -n orionai

# Deployments
kubectl get deployments -n orionai

# Services
kubectl get svc -n orionai

# HPA
kubectl get hpa -n orionai

# Ingress
kubectl get ingress -n orionai
```

### Check Pod Health

```bash
# Describe pod
kubectl describe pod -l app=orionai -n orionai

# Check logs
kubectl logs -l app=orionai -n orionai --tail=100

# Follow logs
kubectl logs -l app=orionai -n orionai -f

# Check specific container
kubectl logs <pod-name> -n orionai -c orionai
```

### Test Health Endpoint

```bash
# Port forward
kubectl port-forward -n orionai svc/orionai-service 8011:8011

# Test in another terminal
curl http://localhost:8011/health
```

### Test Query Endpoint

```bash
curl -X POST http://localhost:8011/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 5}'
```

## Scaling

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment orionai -n orionai --replicas=5

# Verify
kubectl get pods -n orionai
```

### Horizontal Pod Autoscaler

**HPA is deployed by default and will automatically scale based on CPU/memory.**

```bash
# Check HPA status
kubectl get hpa -n orionai

# Describe HPA
kubectl describe hpa orionai-hpa -n orionai

# Watch HPA
kubectl get hpa -n orionai --watch
```

**Adjust HPA:**
```bash
kubectl edit hpa orionai-hpa -n orionai
```

### Vertical Scaling

**Update resource limits:**
```bash
kubectl edit deployment orionai -n orionai
# Modify resources.requests and resources.limits
```

## Monitoring

### Resource Usage

```bash
# Pod metrics
kubectl top pods -n orionai

# Node metrics
kubectl top nodes

# Watch pod metrics
kubectl top pods -n orionai --watch
```

### Events

```bash
# All events
kubectl get events -n orionai --sort-by='.lastTimestamp'

# Watch events
kubectl get events -n orionai --watch
```

### Logs

```bash
# All pods
kubectl logs -l app=orionai -n orionai --tail=100

# Specific pod
kubectl logs <pod-name> -n orionai

# Previous pod instance
kubectl logs <pod-name> -n orionai --previous

# Stream logs
kubectl logs -l app=orionai -n orionai -f --max-log-requests=10
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n orionai

# Describe pod
kubectl describe pod <pod-name> -n orionai

# Check events
kubectl get events -n orionai --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n orionai
```

**Common issues:**
- Image pull errors: Check image name and tag
- Resource limits: Check if nodes have enough resources
- ConfigMap/Secret missing: Verify they exist
- Liveness probe failing: Check health endpoint

### HPA Not Scaling

```bash
# Check HPA status
kubectl describe hpa orionai-hpa -n orionai

# Check metrics-server
kubectl top nodes
kubectl top pods -n orionai

# Check HPA conditions
kubectl get hpa orionai-hpa -n orionai -o yaml
```

**Common issues:**
- metrics-server not installed
- Resource requests not set
- Metrics not available yet (wait 1-2 minutes)

### Service Not Accessible

```bash
# Check service
kubectl get svc orionai-service -n orionai

# Check endpoints
kubectl get endpoints orionai-service -n orionai

# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n orionai -- \
  curl http://orionai-service:8011/health
```

### Ingress Not Working

```bash
# Check ingress
kubectl describe ingress orionai-ingress -n orionai

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Verify DNS
nslookup orionai.example.com

# Test without TLS
curl -H "Host: orionai.example.com" http://<ingress-ip>/health
```

## Updates and Rollbacks

### Update Deployment

**Update image:**
```bash
kubectl set image deployment/orionai orionai=orionai:1.1.0 -n orionai
```

**Update with kubectl:**
```bash
# Edit deployment
kubectl edit deployment orionai -n orionai

# Or apply updated manifest
kubectl apply -f k8s/deployment.yaml
```

**Update with Helm:**
```bash
helm upgrade orionai ./helm/orionai \
  --namespace orionai \
  --set image.tag=1.1.0
```

### Rolling Update

```bash
# Check rollout status
kubectl rollout status deployment/orionai -n orionai

# Watch rollout
kubectl get pods -n orionai --watch
```

### Rollback

```bash
# View rollout history
kubectl rollout history deployment/orionai -n orionai

# Rollback to previous version
kubectl rollout undo deployment/orionai -n orionai

# Rollback to specific revision
kubectl rollout undo deployment/orionai -n orionai --to-revision=2
```

## Cleanup

### Delete Deployment

**kubectl:**
```bash
kubectl delete -f k8s/
kubectl delete namespace orionai
```

**Helm:**
```bash
helm uninstall orionai --namespace orionai
kubectl delete namespace orionai
```

### Delete Specific Resources

```bash
kubectl delete deployment orionai -n orionai
kubectl delete service orionai-service -n orionai
kubectl delete hpa orionai-hpa -n orionai
```

## Production Checklist

- [ ] Update secrets with real values
- [ ] Configure ingress with real domain
- [ ] Set up TLS certificates
- [ ] Configure resource limits based on load testing
- [ ] Enable network policies
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup for Redis PVC
- [ ] Configure pod disruption budget
- [ ] Test disaster recovery
- [ ] Document runbooks
- [ ] Set up alerting
- [ ] Configure autoscaling thresholds
- [ ] Review security policies
- [ ] Enable audit logging

## Advanced Configuration

### GPU Support

**Add GPU node selector:**
```yaml
nodeSelector:
  accelerator: nvidia-gpu
```

**Add GPU resource:**
```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

### External Redis

**Disable internal Redis and configure external:**
```yaml
redis:
  enabled: false
  external:
    enabled: true
    host: redis.external.com
    port: 6379
```

### Multiple Environments

**Create environment-specific values:**
```bash
# values-dev.yaml
replicaCount: 1
autoscaling:
  enabled: false

# values-staging.yaml
replicaCount: 2
autoscaling:
  maxReplicas: 5

# values-prod.yaml
replicaCount: 5
autoscaling:
  maxReplicas: 20
```

**Deploy:**
```bash
helm install orionai-dev ./helm/orionai -f values-dev.yaml --namespace orionai-dev
helm install orionai-staging ./helm/orionai -f values-staging.yaml --namespace orionai-staging
helm install orionai-prod ./helm/orionai -f values-prod.yaml --namespace orionai-prod
```
