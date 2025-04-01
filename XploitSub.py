#!/usr/bin/env python3
"""
XploitSub - Advanced Subdomain Enumeration Tool
Author: xAI's Grok
Version: 1.1
"""

import dns.resolver
import requests
import argparse
import threading
import queue
import time
import sys
import signal
from typing import Set, List, Optional
from urllib.parse import urlparse

class XploitSub:
    def __init__(self, domain: str, wordlist: str, threads: int = 10, timeout: int = 2):
        self.domain = domain
        self.wordlist = wordlist
        self.threads = min(threads, 50)  # Limit max threads
        self.timeout = timeout
        self.found_subdomains: Set[str] = set()
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.total_tested = 0
        self.start_time = 0

    def print_banner(self) -> None:
        """Print startup banner"""
        banner = r"""
██╗  ██╗██████╗ ██╗      ██████╗ ██╗████████╗███████╗██╗   ██╗██████╗ 
╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝██╔════╝██║   ██║██╔══██╗
 ╚███╔╝ ██████╔╝██║     ██║   ██║██║   ██║   ███████╗██║   ██║██████╔╝
 ██╔██╗ ██╔═══╝ ██║     ██║   ██║██║   ██║   ╚════██║██║   ██║██╔══██╗
██╔╝ ██╗██║     ███████╗╚██████╔╝██║   ██║   ███████║╚██████╔╝██████╔╝
╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝ 
        Subdomain Enumeration Tool v1.0 - Created by megoz
        """
        print(banner)
        print(f"[*] Target: {self.domain}")
        print(f"[*] Threads: {self.threads}")
        print(f"[*] Timeout: {self.timeout}s")
        print("[*] Press Ctrl+C to stop enumeration\n")

    def load_wordlist(self) -> List[str]:
        """Load subdomains from wordlist file with validation"""
        try:
            with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            print(f"\n[!] Error: Wordlist file '{self.wordlist}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"\n[!] Error loading wordlist: {str(e)}")
            sys.exit(1)

    def check_subdomain(self, subdomain: str) -> None:
        """Check if subdomain exists using DNS lookup"""
        if self.stop_event.is_set():
            return

        full_domain = f"{subdomain}.{self.domain}"
        
        # Skip invalid subdomains
        if not subdomain or any(c in subdomain for c in './ '):
            return

        try:
            answers = dns.resolver.resolve(full_domain, 'A', lifetime=self.timeout)
            with self.lock:
                self.found_subdomains.add(full_domain)
                print(f"[+] Found: {full_domain}")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass
        except dns.resolver.Timeout:
            pass
        except dns.resolver.NoNameservers:
            pass
        except Exception as e:
            if not self.stop_event.is_set():
                print(f"[-] Error checking {full_domain}: {str(e)}")
        finally:
            with self.lock:
                self.total_tested += 1
                if self.total_tested % 100 == 0:
                    elapsed = time.time() - self.start_time
                    print(f"\r[*] Tested: {self.total_tested} | Found: {len(self.found_subdomains)} | "
                          f"Elapsed: {elapsed:.1f}s", end='', flush=True)

    def worker(self) -> None:
        """Worker thread to process subdomains from queue"""
        while not self.stop_event.is_set():
            try:
                subdomain = self.queue.get_nowait()
                self.check_subdomain(subdomain)
                self.queue.task_done()
            except queue.Empty:
                time.sleep(0.1)
                continue

    def signal_handler(self, signum, frame) -> None:
        """Handle Ctrl+C interrupt"""
        self.stop_event.set()
        print("\n\n[!] Received interrupt signal, stopping threads...")
        elapsed = time.time() - self.start_time
        print(f"\n[*] Enumeration interrupted after {elapsed:.1f} seconds")
        self.show_results()

    def show_results(self) -> None:
        """Display found subdomains and statistics"""
        print("\n[+] Results:")
        print(f"Total tested: {self.total_tested}")
        print(f"Subdomains found: {len(self.found_subdomains)}")
        
        if self.found_subdomains:
            print("\nFound subdomains:")
            for subdomain in sorted(self.found_subdomains):
                print(subdomain)
        
        print("\n[+] Done")

    def enumerate(self) -> None:
        """Main enumeration function"""
        self.print_banner()
        self.start_time = time.time()

        # Register signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Load wordlist
        subdomains = self.load_wordlist()
        if not subdomains:
            print("[!] No valid subdomains found in wordlist")
            return

        print(f"[*] Loaded {len(subdomains)} subdomains from wordlist")

        # Fill queue with subdomains
        for subdomain in subdomains:
            self.queue.put(subdomain)

        # Start worker threads
        threads = []
        for _ in range(min(self.threads, len(subdomains))):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)

        # Wait for queue to be processed or interrupt
        try:
            while not self.queue.empty() and not self.stop_event.is_set():
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

        # Final status update
        elapsed = time.time() - self.start_time
        print(f"\r[*] Tested: {self.total_tested} | Found: {len(self.found_subdomains)} | "
              f"Elapsed: {elapsed:.1f}s", flush=True)

        if not self.stop_event.is_set():
            print("\n[+] Enumeration complete")
            self.show_results()

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain.split(':')[0]  # Remove port if present

def main():
    parser = argparse.ArgumentParser(description="XploitSub - Advanced Subdomain Enumeration Tool")
    parser.add_argument("domain", nargs='?', help="Target domain to enumerate (e.g., example.com)")
    parser.add_argument("-u", "--url", help="Target URL to enumerate (e.g., https://www.example.com)")
    parser.add_argument("-w", "--wordlist", default="subdomains.txt",
                      help="Path to subdomain wordlist file (default: subdomains.txt)")
    parser.add_argument("-t", "--threads", type=int, default=10,
                      help="Number of threads to use (default: 10, max: 50)")
    parser.add_argument("--timeout", type=int, default=2,
                      help="DNS query timeout in seconds (default: 2)")
    
    args = parser.parse_args()

    # Determine domain from either URL or direct domain input
    if args.url:
        domain = get_domain_from_url(args.url)
    elif args.domain:
        domain = args.domain
    else:
        parser.error("Please provide either a domain or URL using -u/--url")

    # Create and run enumerator
    try:
        enumerator = XploitSub(domain, args.wordlist, args.threads, args.timeout)
        enumerator.enumerate()
    except Exception as e:
        print(f"\n[!] Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()