# OrionAI Helm Chart

Production-grade Helm chart for deploying OrionAI to Kubernetes.

## Prerequisites

- Kubernetes 1.24+
- Helm 3.x
- metrics-server (for autoscaling)

## Installation

### Quick Start

```bash
helm install orionai ./orionai --namespace orionai --create-namespace
```

### With Custom Values

```bash
helm install orionai ./orionai \
  --namespace orionai \
  --create-namespace \
  --set image.tag=1.0.0 \
  --set secrets.openaiApiKey="sk-..." \
  --set ingress.hosts[0].host=orionai.yourdomain.com
```

### With Values File

```bash
helm install orionai ./orionai \
  --namespace orionai \
  --create-namespace \
  -f custom-values.yaml
```

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `3` |
| `image.repository` | Image repository | `orionai` |
| `image.tag` | Image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8011` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `nginx` |
| `autoscaling.enabled` | Enable HPA | `true` |
| `autoscaling.minReplicas` | Min replicas | `3` |
| `autoscaling.maxReplicas` | Max replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | CPU target | `70` |
| `autoscaling.targetMemoryUtilizationPercentage` | Memory target | `80` |
| `redis.enabled` | Enable Redis | `true` |
| `redis.persistence.enabled` | Enable Redis persistence | `true` |
| `redis.persistence.size` | Redis PVC size | `5Gi` |
| `resources.requests.cpu` | CPU request | `500m` |
| `resources.requests.memory` | Memory request | `1Gi` |
| `resources.limits.cpu` | CPU limit | `2000m` |
| `resources.limits.memory` | Memory limit | `4Gi` |

### Full Configuration

See [values.yaml](values.yaml) for all available parameters.

## Examples

### Development Environment

```yaml
# values-dev.yaml
replicaCount: 1

autoscaling:
  enabled: false

redis:
  persistence:
    enabled: false

resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 2Gi

ingress:
  enabled: false
```

```bash
helm install orionai-dev ./orionai -f values-dev.yaml --namespace orionai-dev --create-namespace
```

### Production Environment

```yaml
# values-prod.yaml
replicaCount: 5

image:
  tag: "1.0.0"

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70

redis:
  enabled: true
  persistence:
    enabled: true
    size: 20Gi
    storageClass: fast-ssd

resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 4000m
    memory: 8Gi

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "200"
  hosts:
    - host: orionai.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: orionai-tls
      hosts:
        - orionai.yourdomain.com

podDisruptionBudget:
  enabled: true
  minAvailable: 3

networkPolicy:
  enabled: true

secrets:
  openaiApiKey: "sk-..."
  apiKey: "secure-production-key"
```

```bash
helm install orionai ./orionai -f values-prod.yaml --namespace orionai --create-namespace
```

### External Redis

```yaml
redis:
  enabled: false
  external:
    enabled: true
    host: redis.external.com
    port: 6379
```

### GPU Support

```yaml
resources:
  limits:
    nvidia.com/gpu: 1

nodeSelector:
  accelerator: nvidia-gpu
```

## Upgrading

### Upgrade Release

```bash
helm upgrade orionai ./orionai --namespace orionai
```

### Upgrade with New Values

```bash
helm upgrade orionai ./orionai \
  --namespace orionai \
  --set image.tag=1.1.0 \
  --set autoscaling.maxReplicas=20
```

### Upgrade with Values File

```bash
helm upgrade orionai ./orionai \
  --namespace orionai \
  -f values-prod.yaml
```

## Uninstalling

```bash
helm uninstall orionai --namespace orionai
```

## Validation

### Lint Chart

```bash
helm lint ./orionai
```

### Dry Run

```bash
helm install orionai ./orionai \
  --namespace orionai \
  --dry-run --debug
```

### Template Rendering

```bash
helm template orionai ./orionai --namespace orionai
```

### Validate Against Cluster

```bash
helm install orionai ./orionai \
  --namespace orionai \
  --dry-run --debug | kubectl apply --dry-run=client -f -
```

## Troubleshooting

### Check Release Status

```bash
helm status orionai --namespace orionai
```

### View Release History

```bash
helm history orionai --namespace orionai
```

### Get Values

```bash
helm get values orionai --namespace orionai
```

### Get Manifest

```bash
helm get manifest orionai --namespace orionai
```

### Rollback

```bash
helm rollback orionai --namespace orionai
helm rollback orionai 1 --namespace orionai  # to specific revision
```

## Development

### Package Chart

```bash
helm package ./orionai
```

### Update Dependencies

```bash
helm dependency update ./orionai
```

### Test Chart

```bash
helm test orionai --namespace orionai
```
