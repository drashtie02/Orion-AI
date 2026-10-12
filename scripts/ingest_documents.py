import sys
import re
from pathlib import Path
from typing import List, Dict
sys.path.append(str(Path(__file__).parent.parent))

from retrieval.vector_store import VectorStore
from retrieval.bm25 import BM25Index
from core.config import config
from core.logging import setup_logger

logger = setup_logger(__name__)

class DocumentIngestion:
    def __init__(self):
        self.chunk_size = config.chunk_size
        self.overlap_ratio = config.chunk_overlap
        self.chunks = []
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def chunk_text(self, text: str, document_id: str, source_path: str) -> List[Dict]:
        words = text.split()
        overlap_size = int(self.chunk_size * self.overlap_ratio)
        stride = self.chunk_size - overlap_size
        
        chunks = []
        position = 0
        
        for i in range(0, len(words), stride):
            chunk_words = words[i:i + self.chunk_size]
            if not chunk_words:
                break
            
            chunk_text = ' '.join(chunk_words)
            chunks.append({
                'document_id': document_id,
                'chunk_id': f"{document_id}_chunk_{position}",
                'source_path': source_path,
                'position_index': position,
                'text': chunk_text
            })
            position += 1
            
            if i + self.chunk_size >= len(words):
                break
        
        return chunks
    
    def ingest_folder(self, folder_path: str):
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        for file_path in folder.rglob('*.txt'):
            logger.info(f"Processing {file_path.name}")
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            cleaned_text = self.clean_text(text)
            document_id = file_path.stem
            chunks = self.chunk_text(cleaned_text, document_id, str(file_path))
            self.chunks.extend(chunks)
        
        logger.info(f"Created {len(self.chunks)} chunks")
    
    def build_indices(self):
        vector_store = VectorStore()
        vector_store.build_index(self.chunks)
        vector_store.save(config.index_path)
        
        bm25_index = BM25Index()
        bm25_index.build_index(self.chunks)
        bm25_index.save(config.index_path)
        
        logger.info(f"Indices saved to {config.index_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_documents.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    ingestion = DocumentIngestion()
    ingestion.ingest_folder(folder_path)
    ingestion.build_indices()

if __name__ == "__main__":
    main()
