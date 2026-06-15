import xrpl
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import time
from typing import Optional
from dataclasses import dataclass
import multiprocessing
import os

@dataclass
class ScanResult:
    address: str
    seed: str

class AddressScanner:
    def __init__(self, pattern: str, case_sensitive: bool = False, max_workers: Optional[int] = None):
        self.pattern = pattern if case_sensitive else pattern.lower()
        self.case_sensitive = case_sensitive
        self.pattern_length = len(pattern) + 1
        self.running = True
        self.client = xrpl.clients.JsonRpcClient("https://s.altnet.rippletest.net:51234")
        
        # Optimize worker count
        cpu_count = multiprocessing.cpu_count()
        self.max_workers = max_workers or min(32, cpu_count * 2)
        self.batch_size = 1000

    def check_address_batch(self, batch_size: int = 1000) -> Optional[ScanResult]:
        """Generate and check multiple wallet addresses in a batch."""
        for _ in range(batch_size):
            if not self.running:
                return None
                
            wallet = xrpl.wallet.Wallet.create()
            address_slice = wallet.classic_address[1:self.pattern_length]
            if not self.case_sensitive:
                address_slice = address_slice.lower()
            
            if self.pattern in address_slice:
                return ScanResult(wallet.classic_address, wallet.seed)
        return None

    def save_result(self, result: ScanResult):
        with open("found_address.txt", "a", buffering=8192) as f:
            f.write(f"Seed: {result.seed}\n")
            f.write(f"Address: {result.address}\n\n")

    def scan(self, status_interval: int = 5000):
        attempts = 0
        start_time = time.time()
        last_status_time = start_time
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = set()  # Initialize as set
            
            while self.running:
                # Submit batch jobs
                while len(futures) < self.max_workers:
                    futures.add(executor.submit(self.check_address_batch, self.batch_size))
                
                # Process completed futures
                done, not_done = wait(
                    futures, 
                    timeout=0.1,
                    return_when=FIRST_COMPLETED
                )
                
                futures = not_done  # Use remaining futures
                
                for future in done:
                    attempts += self.batch_size
                    try:
                        result = future.result()
                        if result:
                            self.running = False
                            print(f"\nFound matching address: {result.address}")
                            self.save_result(result)
                            return
                    except Exception as e:
                        print(f"Error in worker thread: {e}")
                        continue
                
                # Status update
                current_time = time.time()
                if current_time - last_status_time >= 1.0:
                    elapsed = current_time - start_time
                    rate = attempts / elapsed if elapsed > 0 else 0
                    print(f"Checked {attempts:,} addresses | "
                          f"Rate: {rate:.0f} addresses/sec", end="\r")
                    last_status_time = current_time

def main():
    pattern = input("\nEnter characters to find in address: ")
    case_sensitive = input("Case sensitive search? (y/n): ").lower() == 'y'
    scanner = AddressScanner(pattern, case_sensitive)
    scanner.scan()

if __name__ == "__main__":
    main()