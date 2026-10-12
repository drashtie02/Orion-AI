#!/usr/bin/env python3
"""
Simple Load Testing Script for OrionAI
Measures requests per second and concurrent request handling
"""

import asyncio
import aiohttp
import time
from datetime import datetime
import statistics

BASE_URL = "http://localhost:8011"

# Test queries
QUERIES = [
    "Who is Iron Man?",
    "What are Tony Stark abilities?",
    "Tell me about the arc reactor",
    "What is Stark Tower?",
    "Who is JARVIS?"
]

async def send_request(session, query, request_num):
    """Send a single request and measure response time"""
    start = time.time()
    try:
        async with session.post(
            f"{BASE_URL}/api/v1/query",
            json={"query": query, "top_k": 3},
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            await response.json()
            latency = time.time() - start
            return {
                "success": True,
                "latency": latency,
                "status": response.status,
                "request_num": request_num
            }
    except Exception as e:
        latency = time.time() - start
        return {
            "success": False,
            "latency": latency,
            "error": str(e),
            "request_num": request_num
        }

async def concurrent_test(num_requests, concurrency):
    """Test with specific concurrency level"""
    print(f"\n{'='*60}")
    print(f"Testing: {num_requests} requests with {concurrency} concurrent")
    print(f"{'='*60}")
    
    results = []
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            query = QUERIES[i % len(QUERIES)]
            task = send_request(session, query, i + 1)
            tasks.append(task)
            
            # Control concurrency
            if len(tasks) >= concurrency:
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                tasks = []
                
        # Process remaining tasks
        if tasks:
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
    
    total_time = time.time() - start_time
    
    # Calculate metrics
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    latencies = [r["latency"] for r in successful]
    
    print(f"\n📊 Results:")
    print(f"  Total Requests:     {num_requests}")
    print(f"  Successful:         {len(successful)} ✅")
    print(f"  Failed:             {len(failed)} ❌")
    print(f"  Success Rate:       {len(successful)/num_requests*100:.1f}%")
    print(f"\n⏱️  Performance:")
    print(f"  Total Time:         {total_time:.2f}s")
    print(f"  Requests/Second:    {num_requests/total_time:.2f}")
    print(f"  Requests/Minute:    {(num_requests/total_time)*60:.0f}")
    
    if latencies:
        print(f"\n📈 Latency Stats:")
        print(f"  Min:                {min(latencies):.3f}s")
        print(f"  Max:                {max(latencies):.3f}s")
        print(f"  Mean:               {statistics.mean(latencies):.3f}s")
        print(f"  Median:             {statistics.median(latencies):.3f}s")
        if len(latencies) > 1:
            print(f"  Std Dev:            {statistics.stdev(latencies):.3f}s")
    
    if failed:
        print(f"\n❌ Errors:")
        error_types = {}
        for f in failed:
            error = f.get("error", "Unknown")
            error_types[error] = error_types.get(error, 0) + 1
        for error, count in error_types.items():
            print(f"  {error}: {count}")
    
    return {
        "total_requests": num_requests,
        "successful": len(successful),
        "failed": len(failed),
        "total_time": total_time,
        "rps": num_requests/total_time,
        "rpm": (num_requests/total_time)*60,
        "latencies": latencies
    }

async def main():
    print("🚀 OrionAI Load Testing")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is up
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("✅ Server is healthy\n")
                else:
                    print("⚠️  Server returned non-200 status\n")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test scenarios
    scenarios = [
        {"requests": 10, "concurrency": 1},   # Sequential
        {"requests": 10, "concurrency": 5},   # Low concurrency
        {"requests": 20, "concurrency": 10},  # Medium concurrency
        {"requests": 50, "concurrency": 20},  # High concurrency
    ]
    
    all_results = []
    
    for scenario in scenarios:
        result = await concurrent_test(scenario["requests"], scenario["concurrency"])
        all_results.append(result)
        await asyncio.sleep(2)  # Cool down between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print(f"{'='*60}")
    print(f"\n{'Scenario':<30} {'RPS':<10} {'RPM':<10} {'Avg Latency':<15}")
    print(f"{'-'*65}")
    
    for i, result in enumerate(all_results):
        scenario = scenarios[i]
        avg_latency = statistics.mean(result["latencies"]) if result["latencies"] else 0
        print(f"{scenario['requests']} req @ {scenario['concurrency']} concurrent"
              f"{'':<10} {result['rps']:<10.2f} {result['rpm']:<10.0f} {avg_latency:<15.3f}s")
    
    print(f"\n{'='*60}")
    print("✅ Load testing complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
