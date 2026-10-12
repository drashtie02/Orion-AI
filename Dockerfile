FROM python:3.10-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-cpu.txt ./
RUN pip install --no-cache-dir --user torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --user -r requirements-cpu.txt && \
    pip install --no-cache-dir --user uvicorn[standard] gunicorn

FROM python:3.10-slim

RUN groupadd -r -g 1000 orionai && useradd -r -u 1000 -g orionai orionai

WORKDIR /app

COPY --from=builder /root/.local /home/orionai/.local

COPY --chown=orionai:orionai . .

RUN mkdir -p /app/artifacts /home/orionai/.cache/huggingface && \
    chown -R orionai:orionai /app/artifacts /home/orionai/.cache

USER orionai

ENV PATH=/home/orionai/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV HF_HOME=/home/orionai/.cache/huggingface
ENV TRANSFORMERS_CACHE=/home/orionai/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/home/orionai/.cache/huggingface

# Pre-download models during build
RUN python scripts/download_models.py

EXPOSE 8011

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8011/health', timeout=5)" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011", "--workers", "1"]
