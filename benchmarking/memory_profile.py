import tracemalloc
import asyncio
import httpx
import time
import json
from pathlib import Path
from typing import Dict, List

class MemoryProfiler:
    def __init__(self, base_url: str = "http://localhost:8011"):
        self.base_url = base_url
        self.results = []
    
    def get_memory_snapshot(self) -> Dict:
        current, peak = tracemalloc.get_traced_memory()
        return {
            'current_mb': round(current / 1024 / 1024, 2),
            'peak_mb': round(peak / 1024 / 1024, 2)
        }
    
    async def run_load_test(self, num_requests: int = 1000):
        tracemalloc.start()
        
        baseline = self.get_memory_snapshot()
        self.results.append({
            'stage': 'baseline',
            'memory': baseline,
            'requests_completed': 0
        })
        
        print(f"Baseline memory: {baseline['current_mb']} MB (peak: {baseline['peak_mb']} MB)")
        
        queries = [
            "What is machine learning?",
            "Explain neural networks",
            "What is cloud computing?",
            "How does RAG work?",
            "What is vector search?"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(num_requests):
                try:
                    query = queries[i % len(queries)]
                    response = await client.post(
                        f"{self.base_url}/api/v1/query",
                        json={"query": query, "top_k": 5}
                    )
                    
                    if (i + 1) % 100 == 0:
                        snapshot = self.get_memory_snapshot()
                        self.results.append({
                            'stage': f'after_{i+1}_requests',
                            'memory': snapshot,
                            'requests_completed': i + 1
                        })
                        print(f"After {i+1} requests: {snapshot['current_mb']} MB (peak: {snapshot['peak_mb']} MB)")
                    
                    if i < 10:
                        await asyncio.sleep(0.1)
                
                except Exception as e:
                    print(f"Request {i+1} failed: {e}")
        
        final = self.get_memory_snapshot()
        self.results.append({
            'stage': 'final',
            'memory': final,
            'requests_completed': num_requests
        })
        
        print(f"\\nFinal memory: {final['current_mb']} MB (peak: {final['peak_mb']} MB)")
        print(f"Memory increase: {final['current_mb'] - baseline['current_mb']} MB")
        
        tracemalloc.stop()
    
    def generate_report(self) -> Dict:
        if len(self.results) < 2:
            return {'error': 'Insufficient data'}
        
        baseline = self.results[0]['memory']
        final = self.results[-1]['memory']
        
        memory_increase = final['current_mb'] - baseline['current_mb']
        peak_increase = final['peak_mb'] - baseline['peak_mb']
        
        memory_per_request = memory_increase / self.results[-1]['requests_completed'] if self.results[-1]['requests_completed'] > 0 else 0
        
        potential_leak = memory_increase > 50 or memory_per_request > 0.1
        
        return {
            'baseline_memory_mb': baseline['current_mb'],
            'final_memory_mb': final['current_mb'],
            'peak_memory_mb': final['peak_mb'],
            'memory_increase_mb': round(memory_increase, 2),
            'peak_increase_mb': round(peak_increase, 2),
            'total_requests': self.results[-1]['requests_completed'],
            'memory_per_request_kb': round(memory_per_request * 1024, 2),
            'potential_memory_leak': potential_leak,
            'snapshots': self.results,
            'recommendations': self._generate_recommendations(memory_increase, memory_per_request)
        }
    
    def _generate_recommendations(self, memory_increase: float, memory_per_request: float) -> List[str]:
        recommendations = []
        
        if memory_increase > 100:
            recommendations.append("High memory increase detected. Review caching strategy and ensure proper cleanup.")
        
        if memory_per_request > 0.1:
            recommendations.append("Memory per request is high. Consider reducing context size or implementing streaming.")
        
        if memory_increase > 50:
            recommendations.append("Moderate memory increase. Monitor for memory leaks in long-running processes.")
        
        if not recommendations:
            recommendations.append("Memory usage is within acceptable limits.")
        
        return recommendations
    
    def save_report(self, output_path: str = "artifacts/memory_profile_report.json"):
        report = self.generate_report()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\\nReport saved to {output_path}")
        return report

async def main():
    print("Starting memory profiling...")
    print("Ensure OrionAI is running on http://localhost:8011")
    print()
    
    profiler = MemoryProfiler()
    
    await profiler.run_load_test(num_requests=1000)
    
    report = profiler.save_report()
    
    print("\\n" + "="*60)
    print("MEMORY PROFILING REPORT")
    print("="*60)
    print(f"Baseline Memory: {report['baseline_memory_mb']} MB")
    print(f"Final Memory: {report['final_memory_mb']} MB")
    print(f"Peak Memory: {report['peak_memory_mb']} MB")
    print(f"Memory Increase: {report['memory_increase_mb']} MB")
    print(f"Total Requests: {report['total_requests']}")
    print(f"Memory per Request: {report['memory_per_request_kb']} KB")
    print(f"Potential Memory Leak: {'YES' if report['potential_memory_leak'] else 'NO'}")
    print("\\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
