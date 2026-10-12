import pytest
from unittest.mock import Mock, patch
import numpy as np
from retrieval.bm25 import BM25Index

class TestBM25Index:
    def test_initialization(self):
        index = BM25Index()
        assert index is not None
    
    def test_build_index(self):
        index = BM25Index()
        chunks = [
            {'text': 'machine learning', 'chunk_id': '0'},
            {'text': 'deep learning', 'chunk_id': '1'}
        ]
        index.build_index(chunks)
        assert index.metadata is not None
    
    def test_search(self):
        index = BM25Index()
        chunks = [
            {'text': 'machine learning is great', 'chunk_id': '0'},
            {'text': 'deep learning uses neural networks', 'chunk_id': '1'}
        ]
        index.build_index(chunks)
        results = index.search('machine learning', top_k=1)
        assert len(results) <= 1
    
    def test_search_empty_index(self):
        index = BM25Index()
        results = index.search('test', top_k=5)
        assert results == []
