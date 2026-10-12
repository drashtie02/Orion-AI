import pytest
from unittest.mock import Mock, patch

@pytest.mark.integration
class TestFullPipeline:
    @patch('retrieval.hybrid.HybridRetriever')
    @patch('llm.router.LLMRouter')
    @patch('evaluation.evaluator.Evaluator')
    def test_complete_query_flow(self, mock_eval_class, mock_llm_class, mock_retriever_class):
        mock_retriever = Mock()
        mock_retriever.search = Mock(return_value=[
            {
                'chunk': {
                    'text': 'Machine learning is a subset of AI',
                    'source_path': 'ml.txt',
                    'chunk_id': 'chunk_0'
                },
                'vector_score': 0.95,
                'bm25_score': 0.88,
                'hybrid_score': 0.915
            }
        ])
        mock_retriever.embedding_model = Mock()
        
        mock_llm = Mock()
        mock_llm.generate = Mock(return_value={
            'text': 'Machine learning is a method of data analysis.',
            'tokens_input': 150,
            'tokens_output': 75,
            'model_name': 'test_model'
        })
        mock_llm.count_tokens = Mock(return_value=10)
        mock_llm.model_name = 'test_model'
        
        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value={
            'faithfulness': {'faithfulness_score': 0.92},
            'relevance': {'relevance_score': 0.89},
            'hallucination': {'hallucination_risk': 0.05},
            'confidence_score': 0.90
        })
        
        mock_retriever_class.return_value = mock_retriever
        mock_llm_class.return_value = mock_llm
        mock_eval_class.return_value = mock_evaluator
        
        from core.orchestrator import Orchestrator
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm,
            mock_evaluator,
            critic_threshold=0.6,
            retry_enabled=False
        )
        
        result = orchestrator.execute("What is machine learning?", top_k=5)
        
        assert result is not None
        assert 'answer' in result
        assert 'sources' in result
        assert 'evaluation' in result
        assert 'trace' in result
        assert len(result['sources']) > 0
        assert result['evaluation']['confidence_score'] == 0.90
        
        mock_retriever.search.assert_called_once()
        mock_llm.generate.assert_called()
        mock_evaluator.evaluate.assert_called()
    
    @patch('retrieval.hybrid.HybridRetriever')
    @patch('llm.router.LLMRouter')
    @patch('evaluation.evaluator.Evaluator')
    def test_pipeline_with_retry(self, mock_eval_class, mock_llm_class, mock_retriever_class):
        mock_retriever = Mock()
        mock_retriever.search = Mock(return_value=[
            {
                'chunk': {
                    'text': 'Test content',
                    'source_path': 'test.txt',
                    'chunk_id': 'chunk_0'
                },
                'vector_score': 0.9,
                'bm25_score': 0.8,
                'hybrid_score': 0.85
            }
        ])
        mock_retriever.embedding_model = Mock()
        
        mock_llm = Mock()
        mock_llm.generate = Mock(return_value={
            'text': 'Low confidence answer',
            'tokens_input': 100,
            'tokens_output': 50,
            'model_name': 'test_model'
        })
        mock_llm.count_tokens = Mock(return_value=10)
        mock_llm.model_name = 'test_model'
        
        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value={
            'faithfulness': {'faithfulness_score': 0.4},
            'relevance': {'relevance_score': 0.3},
            'hallucination': {'hallucination_risk': 0.3},
            'confidence_score': 0.35
        })
        
        mock_retriever_class.return_value = mock_retriever
        mock_llm_class.return_value = mock_llm
        mock_eval_class.return_value = mock_evaluator
        
        from core.orchestrator import Orchestrator
        
        orchestrator = Orchestrator(
            mock_retriever,
            mock_llm,
            mock_evaluator,
            critic_threshold=0.6,
            retry_enabled=True
        )
        
        result = orchestrator.execute("Test query", top_k=5)
        
        assert result is not None
        assert 'trace' in result
        
        trace_steps = [step['step'] for step in result['trace']]
        assert 'retry_reasoning' in trace_steps or 'reasoning' in trace_steps
