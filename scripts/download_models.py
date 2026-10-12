#!/usr/bin/env python3
"""Pre-download models for Docker image"""
import os
from sentence_transformers import SentenceTransformer

# Set cache directory
cache_dir = os.environ.get('SENTENCE_TRANSFORMERS_HOME', '/home/orionai/.cache/huggingface')
os.makedirs(cache_dir, exist_ok=True)

# Download embedding model
print("Downloading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', cache_folder=cache_dir)
print(f"Model downloaded to {cache_dir}")
print("Model ready for use")
