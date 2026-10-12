import os
import random
from locust import HttpUser, task, between

class OrionAIUser(HttpUser):
    wait_time = between(1, 3)
    
    queries = [
        'What is machine learning?',
        'Explain neural networks',
        'How does deep learning work?',
        'What are transformers in AI?',
        'Describe reinforcement learning',
        'What is natural language processing?',
        'Explain computer vision',
        'How do convolutional neural networks work?',
        'What is transfer learning?',
        'Describe gradient descent optimization',
    ]
    
    def on_start(self):
        self.api_key = os.getenv('API_KEY', '')
        self.headers = {'Content-Type': 'application/json'}
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key
    
    @task
    def query_rag(self):
        query = random.choice(self.queries)
        payload = {
            'query': query,
            'top_k': 5
        }
        
        with self.client.post(
            '/api/v1/query',
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'answer' in data:
                        response.success()
                    else:
                        response.failure('No answer in response')
                except Exception as e:
                    response.failure(f'Invalid JSON: {e}')
            else:
                response.failure(f'Status code: {response.status_code}')
    
    @task(1)
    def health_check(self):
        with self.client.get('/health', catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f'Health check failed: {response.status_code}')
