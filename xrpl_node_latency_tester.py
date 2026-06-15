import asyncio
import aiohttp
import time
import statistics
import logging
from datetime import datetime
from typing import List, Dict, Any
import websockets

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class XRPLNodeTester:
    def __init__(self):
        self.nodes = [
            {
                "url": "https://xrplcluster.com/rpc",
                "ws": "wss://xrplcluster.com/",
                "location": "Global",
                "type": "Public Cluster"
            },
            {
                "url": "https://s1.ripple.com:51234/",
                "ws": "wss://s1.ripple.com/",
                "location": "North America",
                "type": "Ripple"
            },
            {
                "url": "https://s2.ripple.com:51234/",
                "ws": "wss://s2.ripple.com/",
                "location": "North America",
                "type": "Ripple"
            },
            {
                "url": "https://xrpl.ws/rpc",
                "ws": "wss://xrpl.ws/",
                "location": "Global",
                "type": "Community"
            },
            {
                "url": "https://xrpl.link/rpc",
                "ws": "wss://xrpl.link/",
                "location": "Europe",
                "type": "Community"
            },
            {
                "url": "http://23.88.78.185:5005",
                "ws": "ws://23.88.78.185:6005",
                "location": "Germany",
                "type": "Private Node"
            }
        ]
        self.test_duration = 60  # 1 minute test per node
        self.request_interval = 1  # 1 second between requests

    async def test_node(self, session: aiohttp.ClientSession, node: Dict[str, str]) -> Dict[str, Any]:
        """Test both HTTP and WebSocket connections for a node"""
        results = {
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limits": 0,
            "latencies": [],
            "ws_successful": 0,
            "ws_failed": 0
        }

        # Test HTTP
        payload = {
            "method": "ledger_current",
            "params": [{}]
        }

        logging.info(f"\nTesting {node['url']}...")
        start_time = time.time()
        test_count = 0

        # HTTP Testing
        while time.time() - start_time < self.test_duration:
            try:
                request_start = time.time()
                async with session.post(node["url"], json=payload) as response:
                    latency = (time.time() - request_start) * 1000  # Convert to ms
                    test_count += 1
                    
                    if response.status == 200:
                        results["successful_requests"] += 1
                        results["latencies"].append(latency)
                        if test_count % 5 == 0:  # Update every 5 requests
                            logging.info(f"HTTP Test #{test_count}: Latency {latency:.2f}ms")
                    elif response.status == 429:
                        results["rate_limits"] += 1
                        logging.warning(f"Rate limit hit on test #{test_count}")
                    else:
                        results["failed_requests"] += 1
                        logging.warning(f"Request failed with status {response.status}")
                        
            except Exception as e:
                results["failed_requests"] += 1
                logging.error(f"HTTP request error: {str(e)}")
                
            await asyncio.sleep(self.request_interval)

        # WebSocket Testing
        logging.info(f"Testing WebSocket connection for {node['ws']}")
        try:
            async with websockets.connect(node["ws"]) as websocket:
                await websocket.send('{"command": "subscribe", "streams": ["ledger"]}')
                ws_start_time = time.time()
                
                while time.time() - ws_start_time < 10:  # 10 second WebSocket test
                    try:
                        await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        results["ws_successful"] += 1
                    except asyncio.TimeoutError:
                        results["ws_failed"] += 1
                    except Exception:
                        results["ws_failed"] += 1
                        
        except Exception as e:
            logging.error(f"WebSocket connection error: {str(e)}")
            results["ws_failed"] += 1

        return results

    def calculate_score(self, results: Dict[str, Any]) -> float:
        """Calculate a score for the node based on all metrics"""
        try:
            total_requests = results["successful_requests"] + results["failed_requests"]
            if total_requests == 0:
                return 0

            success_rate = results["successful_requests"] / total_requests * 100
            avg_latency = statistics.mean(results["latencies"]) if results["latencies"] else 1000
            latency_score = min(100, 10000 / avg_latency)  # Lower latency = higher score
            
            rate_limit_score = 100 - (results["rate_limits"] / total_requests * 100)
            
            ws_total = results["ws_successful"] + results["ws_failed"]
            ws_score = (results["ws_successful"] / ws_total * 100) if ws_total > 0 else 0

            # Weight the scores
            final_score = (
                success_rate * 0.4 +    # 40% weight for success rate
                latency_score * 0.3 +   # 30% weight for latency
                rate_limit_score * 0.2 + # 20% weight for rate limit resistance
                ws_score * 0.1          # 10% weight for WebSocket reliability
            )
            
            return final_score
            
        except Exception as e:
            logging.error(f"Error calculating score: {str(e)}")
            return 0

    async def run_tests(self):
        """Run tests on all nodes"""
        async with aiohttp.ClientSession() as session:
            node_results = []
            
            for node in self.nodes:
                logging.info(f"\nStarting tests for {node['url']}")
                results = await self.test_node(session, node)
                
                score = self.calculate_score(results)
                
                # Calculate and log statistics
                avg_latency = statistics.mean(results["latencies"]) if results["latencies"] else 0
                min_latency = min(results["latencies"]) if results["latencies"] else 0
                max_latency = max(results["latencies"]) if results["latencies"] else 0
                
                summary = {
                    "node": node,
                    "score": score,
                    "avg_latency": avg_latency,
                    "min_latency": min_latency,
                    "max_latency": max_latency,
                    "success_rate": (results["successful_requests"] / (results["successful_requests"] + results["failed_requests"])) * 100 if (results["successful_requests"] + results["failed_requests"]) > 0 else 0,
                    "rate_limits": results["rate_limits"],
                    "ws_reliability": (results["ws_successful"] / (results["ws_successful"] + results["ws_failed"])) * 100 if (results["ws_successful"] + results["ws_failed"]) > 0 else 0
                }
                
                node_results.append(summary)
                
                logging.info(f"""
                                Test Results for {node['url']}:
                                Location: {node['location']}
                                Score: {score:.2f}/100
                                Average Latency: {avg_latency:.2f}ms
                                Min Latency: {min_latency:.2f}ms
                                Max Latency: {max_latency:.2f}ms
                                Success Rate: {summary['success_rate']:.2f}%
                                Rate Limits Hit: {results['rate_limits']}
                                WebSocket Reliability: {summary['ws_reliability']:.2f}%
                                """)

            # Sort and display final rankings
            node_results.sort(key=lambda x: x["score"], reverse=True)
            
            logging.info("\n=== Final Rankings ===")
            for i, result in enumerate(node_results, 1):
                logging.info(f"{i}. {result['node']['url']} (Score: {result['score']:.2f})")

            return node_results

async def main():
    tester = XRPLNodeTester()
    results = await tester.run_tests()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"xrpl_node_test_results_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write("XRPL Node Test Results\n")
        f.write(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in results:
            f.write(f"""
Node: {result['node']['url']}
Location: {result['node']['location']}
Score: {result['score']:.2f}/100
Average Latency: {result['avg_latency']:.2f}ms
Success Rate: {result['success_rate']:.2f}%
WebSocket Reliability: {result['ws_reliability']:.2f}%
{'=' * 50}
""")
    
    logging.info(f"\nDetailed results saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())