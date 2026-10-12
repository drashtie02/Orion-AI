# Demo Recording Steps

## Prerequisites

- OrionAI running locally or on Kubernetes
- Ollama service running with llama2 model
- Redis running
- k6 installed for load testing
- Screen recording software installed

## Recording Tools

### Linux
- **Peek** (recommended): Simple GIF recorder
  ```bash
  sudo apt install peek
  ```
- **SimpleScreenRecorder**: Full-featured
  ```bash
  sudo apt install simplescreenrecorder
  ```

### macOS
- **Kap** (recommended): Open-source screen recorder
  ```bash
  brew install --cask kap
  ```
- **QuickTime Player**: Built-in

### Windows
- **ScreenToGif**: Free and powerful
  - Download: https://www.screentogif.com/
- **OBS Studio**: Professional option
  - Download: https://obsproject.com/

### CLI Alternative (All Platforms)
```bash
# Record with ffmpeg
ffmpeg -f x11grab -s 1920x1080 -i :0.0 -r 30 demo.mp4

# Convert to GIF
ffmpeg -i demo.mp4 -vf "fps=10,scale=1024:-1:flags=lanczos" demo.gif
```

---

## Recording Steps

### Setup (Before Recording)

1. **Start Ollama**
   ```bash
   ollama serve
   ollama pull llama2
   ```

2. **Start Redis**
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Start OrionAI**
   ```bash
   python main.py
   ```

4. **Verify Health**
   ```bash
   curl http://localhost:8011/health
   ```

5. **Clear Terminal**
   ```bash
   clear
   ```

6. **Prepare Commands**
   - Open `demo_commands.sh` in editor
   - Have commands ready to copy-paste

---

### Recording Sequence

#### Scene 1: Streaming Response (30-40 seconds)

**Terminal Setup:**
- Font size: 14-16pt
- Window size: 1024x768 or larger
- Dark theme recommended

**Actions:**
1. Start recording
2. Run streaming query:
   ```bash
   curl -X POST http://localhost:8011/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is machine learning?", "stream": true}'
   ```
3. Let tokens stream for 10-15 seconds
4. Stop recording

**Expected Output:**
- SSE events with tokens appearing in real-time
- Sources and evaluation metrics at end

---

#### Scene 2: Cache Hit (15-20 seconds)

**Actions:**
1. Start recording
2. Run same query again (non-streaming):
   ```bash
   curl -X POST http://localhost:8011/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is machine learning?", "top_k": 5}'
   ```
3. Show instant response
4. Stop recording

**Expected Output:**
- Immediate response (< 100ms)
- Same answer from cache

---

#### Scene 3: Rate Limiting (20 seconds)

**Actions:**
1. Start recording
2. Run rapid requests:
   ```bash
   for i in {1..10}; do
     curl -X POST http://localhost:8011/api/v1/query \
       -H "Content-Type: application/json" \
       -d '{"query": "Test query '$i'"}' &
   done
   wait
   ```
3. Show 429 errors
4. Stop recording

**Expected Output:**
- First few requests succeed
- Later requests return 429 Too Many Requests

---

#### Scene 4: Load Test (60 seconds)

**Terminal Setup:**
- Split screen: k6 output + kubectl watch

**Actions:**
1. Start recording
2. In terminal 1, run k6:
   ```bash
   cd load-testing
   BASE_URL=http://localhost:8011 k6 run k6-script.js --duration 60s
   ```
3. In terminal 2 (if on K8s), watch pods:
   ```bash
   kubectl get pods -n orionai -w
   ```
4. Let test run for 60 seconds
5. Stop recording

**Expected Output:**
- k6 metrics showing throughput, latency
- Pods scaling up (if on K8s)
- No errors or minimal error rate

---

#### Scene 5: Kubernetes Scaling (Optional, 40 seconds)

**Prerequisites:**
- OrionAI deployed on Kubernetes
- HPA enabled

**Actions:**
1. Start recording
2. Show initial state:
   ```bash
   kubectl get pods -n orionai
   kubectl get hpa -n orionai
   ```
3. Start load test in background
4. Watch scaling:
   ```bash
   kubectl get pods -n orionai -w
   ```
5. Show HPA metrics:
   ```bash
   kubectl get hpa -n orionai --watch
   ```
6. Stop recording after scale-up

**Expected Output:**
- Pods increase from 3 to 5-8
- HPA shows CPU utilization and target
- Scaling completes in 45-60 seconds

---

## Post-Recording

### Optimization

**Reduce file size:**
```bash
# Using gifsicle
gifsicle -O3 --colors 256 demo.gif -o demo_optimized.gif

# Using ffmpeg
ffmpeg -i demo.gif -vf "fps=10,scale=800:-1:flags=lanczos" demo_optimized.gif
```

**Convert to WebM (better quality, smaller size):**
```bash
ffmpeg -i demo.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 demo.webm
```

### Naming Convention

- `demo_streaming.gif` - Streaming response demo
- `demo_cache.gif` - Cache hit demo
- `demo_loadtest.gif` - Load testing demo
- `demo_scaling.gif` - Kubernetes autoscaling demo

### File Size Targets

- GIF: < 10 MB (GitHub limit: 10 MB)
- WebM: < 5 MB
- MP4: < 20 MB

---

## Troubleshooting

### Recording Issues

**Problem:** GIF too large  
**Solution:** Reduce FPS to 10, scale to 800px width

**Problem:** Choppy playback  
**Solution:** Use WebM instead of GIF

**Problem:** Text unreadable  
**Solution:** Increase terminal font size to 16pt+

### Demo Issues

**Problem:** Streaming not working  
**Solution:** Check Ollama is running, verify model loaded

**Problem:** Cache always misses  
**Solution:** Check Redis connection, verify cache TTL

**Problem:** Rate limit not triggering  
**Solution:** Reduce rate limit in config.yaml for demo

**Problem:** HPA not scaling  
**Solution:** Verify metrics-server installed, check CPU load

---

## Tips for Professional Recording

1. **Clean terminal**: Remove clutter, use minimal prompt
2. **Consistent timing**: Don't rush, let outputs display fully
3. **Highlight key info**: Use comments or echo statements
4. **Test first**: Do a dry run before recording
5. **Edit if needed**: Trim dead time, speed up slow parts
6. **Add captions**: Consider adding text overlays for clarity
7. **Keep it short**: 30-60 seconds per scene maximum
8. **Show real output**: No mocking, no fake data

---

## Alternative: Asciinema

For terminal-only demos, use asciinema:

```bash
# Install
pip install asciinema

# Record
asciinema rec demo.cast

# Upload
asciinema upload demo.cast

# Convert to GIF
docker run --rm -v $PWD:/data asciinema/asciicast2gif demo.cast demo.gif
```

Benefits:
- Smaller file size
- Text remains selectable
- Easy to edit
- Embeddable in README
