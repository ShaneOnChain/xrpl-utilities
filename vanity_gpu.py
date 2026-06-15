import os
import sys
import hashlib
import base58
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import psutil
from fastecdsa import keys, curve
import ed25519

XRPL_ALPHABET = "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"
XRPL_SEED_PREFIX = b'\x21'

def generate_xrp_address():
    """Generate an XRPL-compliant seed and address using official derivation."""
    if sys.version_info.minor < 6:
        from random import SystemRandom
        randbits = SystemRandom().getrandbits
    else:
        from secrets import randbits
    
    # Generate random seed
    seed_bytes = randbits(16*8).to_bytes(16, byteorder="big")
    seed = Seed(seed_bytes.hex())
    
    # Get the secp256k1 keys
    address = seed.encode_secp256k1_public_base58()
    
    return {
        "seed": seed.encode_base58(),
        "private_key": seed.secp256k1_secret_key.hex().upper(),
        "public_key": seed.secp256k1_public_key.hex().upper(),
        "address": address
    }

def save_result_to_file(result):
    """Save the matching wallet details to a file."""
    with open("found_address.txt", "a") as file:
        file.write(f"Seed: {result['seed']}\n")
        file.write(f"Address: {result['address']}\n\n")

def find_address(pattern, case_sensitive=False, start_only=False, max_workers=4):
    """Search for an XRP address containing the specified pattern."""
    if not case_sensitive:
        pattern = pattern.lower()

    print(f"Starting search for pattern: {pattern}")
    print(f"Case {'Sensitive' if case_sensitive else 'Insensitive'}")
    print(f"Position: {'Start only' if start_only else 'Anywhere'}")

    attempts = 0
    start_time = time.time()
    running = True
    
    # Add status update thread
    def status_update():
        last_attempts = 0
        last_time = start_time
        while running:
            current_time = time.time()
            elapsed = current_time - last_time
            if (elapsed >= 1.0):  # Update every second
                current_rate = (attempts - last_attempts) / elapsed
                total_elapsed = current_time - start_time
                avg_rate = attempts / total_elapsed if total_elapsed > 0 else 0
                print(f"Checked {attempts:,} addresses | "
                      f"Current: {current_rate:.0f}/s | "
                      f"Average: {avg_rate:.0f}/s", end="\r")
                last_attempts = attempts
                last_time = current_time
            time.sleep(0.1)

    status_thread = threading.Thread(target=status_update, daemon=True)
    status_thread.start()

    def worker():
        nonlocal attempts
        while running:
            wallet = generate_xrp_address()
            address = wallet["address"]
            if not case_sensitive:
                address = address.lower()
            attempts += 1
            
            # Check if pattern matches based on position preference
            if start_only:
                if address[1:].startswith(pattern):  # Check right after 'r'
                    return wallet
            else:
                if pattern in address[1:]:  # Check anywhere after 'r'
                    return wallet
        return None

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker) for _ in range(max_workers)]
            for future in futures:
                result = future.result()
                if result:
                    running = False
                    elapsed_time = time.time() - start_time
                    print(f"\nMatch found!")
                    print(f"Seed: {result['seed']}")
                    print(f"Address: {result['address']}")
                    print(f"Attempts: {attempts:,}")
                    print(f"Total Time: {elapsed_time:.2f} seconds")
                    print(f"Final Speed: {attempts/elapsed_time:.0f} addresses/sec")
                    save_result_to_file(result)
                    return
    finally:
        running = False

def main():
    print("\nXRP Address Finder")
    print("===================")
    
    pattern = input("Enter the pattern to search for in the address: ").strip()
    if not all(c in XRPL_ALPHABET for c in pattern):
        print("Invalid pattern. Only XRPL Base58 characters are allowed.")
        return

    case_sensitive = input("Case sensitive search? (y/n): ").strip().lower() == "y"
    start_only = input("Search at start of address only? (y/n): ").strip().lower() == "y"
    max_workers = min(psutil.cpu_count(logical=True), 8)  # Use up to 8 threads

    try:
        find_address(pattern, case_sensitive=case_sensitive, start_only=start_only, max_workers=max_workers)
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    finally:
        print("Exiting...")

if __name__ == "__main__":
    main()
