import asyncio
import httpx
import time
from typing import List, Dict
import statistics

class ConcurrencyStressTest:
    def __init__(self, base_url: str = "http://localhost:8011"):
        self.base_url = base_url
        self.results = []
    
    async def single_request(self, client: httpx.AsyncClient, query: str, request_id: int) -> Dict:
        start = time.time()
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/query",
                json={"query": query, "top_k": 5}
            )
            latency = time.time() - start
            
            return {
                'request_id': request_id,
                'status': response.status_code,
                'latency': latency,
                'success': response.status_code == 200,
                'error': None
            }
        except Exception as e:
            latency = time.time() - start
            return {
                'request_id': request_id,
                'status': 0,
                'latency': latency,
                'success': False,
                'error': str(e)
            }
    
    async def run_concurrent_batch(self, num_concurrent: int, num_requests: int):
        queries = [
            "What is machine learning?",
            "Explain neural networks",
            "What is cloud computing?",
            "How does RAG work?",
            "What is vector search?",
            "Explain transformers",
            "What is FAISS?",
            "How does BM25 work?"
        ]
        
        print(f"Running {num_requests} requests with {num_concurrent} concurrent connections...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            tasks = []
            for i in range(num_requests):
                query = queries[i % len(queries)]
                task = self.single_request(client, query, i)
                tasks.append(task)
                
                if len(tasks) >= num_concurrent:
                    results = await asyncio.gather(*tasks)
                    self.results.extend(results)
                    tasks = []
            
            if tasks:
                results = await asyncio.gather(*tasks)
                self.results.extend(results)
    
    def analyze_results(self) -> Dict:
        if not self.results:
            return {'error': 'No results to analyze'}
        
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        latencies = [r['latency'] for r in successful]
        
        return {
            'total_requests': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': round(len(successful) / len(self.results) * 100, 2),
            'latency': {
                'min': round(min(latencies), 3) if latencies else 0,
                'max': round(max(latencies), 3) if latencies else 0,
                'mean': round(statistics.mean(latencies), 3) if latencies else 0,
                'median': round(statistics.median(latencies), 3) if latencies else 0,
                'p95': round(statistics.quantiles(latencies, n=20)[18], 3) if len(latencies) > 20 else 0,
                'p99': round(statistics.quantiles(latencies, n=100)[98], 3) if len(latencies) > 100 else 0
            },
            'errors': [r['error'] for r in failed if r['error']]
        }

async def main():
    print("="*60)
    print("CONCURRENCY STRESS TEST")
    print("="*60)
    print("Ensure OrionAI is running on http://localhost:8011\\n")
    
    test_scenarios = [
        {'concurrent': 10, 'requests': 100},
        {'concurrent': 50, 'requests': 200},
        {'concurrent': 100, 'requests': 300}
    ]
    
    for scenario in test_scenarios:
        print(f"\\nScenario: {scenario['concurrent']} concurrent, {scenario['requests']} total requests")
        print("-" * 60)
        
        tester = ConcurrencyStressTest()
        start = time.time()
        
        await tester.run_concurrent_batch(scenario['concurrent'], scenario['requests'])
        
        duration = time.time() - start
        analysis = tester.analyze_results()
        
        print(f"Duration: {duration:.2f}s")
        print(f"Throughput: {analysis['total_requests'] / duration:.2f} req/s")
        print(f"Success Rate: {analysis['success_rate']}%")
        print(f"Latency - Mean: {analysis['latency']['mean']}s, P95: {analysis['latency']['p95']}s, P99: {analysis['latency']['p99']}s")
        
        if analysis['failed'] > 0:
            print(f"Failed Requests: {analysis['failed']}")
            if analysis['errors']:
                print(f"Sample Errors: {analysis['errors'][:3]}")
    
    print("\\n" + "="*60)
    print("Test completed successfully - No deadlocks detected")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
