"""Dataset loader for retrieval evaluation."""
import json
from pathlib import Path
from typing import List, Dict, Set


class EvaluationDataset:
    """Loads and validates evaluation dataset with ground truth relevance."""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.queries = []
        self._load()
        self._validate()
    
    def _load(self):
        """Load dataset from JSON file."""
        with open(self.dataset_path, 'r') as f:
            self.queries = json.load(f)
    
    def _validate(self):
        """Validate dataset structure."""
        required_fields = {'query_id', 'query', 'relevant_chunks'}
        
        for i, query_data in enumerate(self.queries):
            missing = required_fields - set(query_data.keys())
            if missing:
                raise ValueError(f"Query {i} missing fields: {missing}")
            
            if not isinstance(query_data['relevant_chunks'], list):
                raise ValueError(f"Query {i}: relevant_chunks must be a list")
            
            if not query_data['relevant_chunks']:
                raise ValueError(f"Query {i}: relevant_chunks cannot be empty")
    
    def get_queries(self) -> List[Dict]:
        """Return all queries."""
        return self.queries
    
    def get_query_by_id(self, query_id: str) -> Dict:
        """Get specific query by ID."""
        for query_data in self.queries:
            if query_data['query_id'] == query_id:
                return query_data
        raise ValueError(f"Query ID {query_id} not found")
    
    def get_relevant_chunks(self, query_id: str) -> Set[str]:
        """Get set of relevant chunk IDs for a query."""
        query_data = self.get_query_by_id(query_id)
        return set(query_data['relevant_chunks'])
    
    def __len__(self) -> int:
        return len(self.queries)
    
    def __iter__(self):
        return iter(self.queries)
