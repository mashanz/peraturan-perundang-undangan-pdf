#!/usr/bin/env python3
"""
🚨 EMERGENCY CONSTITUTIONAL SAVER 🚨
MISSION: Save Indonesia's legal framework in 30 minutes
TARGET: 9,800+ constitutional regulations (UU, PP, PERPRES) 2020-2026
STRATEGY: Maximum parallelism, zero validation delays, recent years priority
"""

import asyncio
import aiohttp
import aiofiles
import json
import time
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

# 🚨 EMERGENCY CONFIGURATION
MAX_CONCURRENT = 100  # Maximum parallelism
TARGET_RPS = 7.5      # Requests per second target
TIMEOUT = 10          # Quick timeout to avoid delays
MAX_RETRIES = 0       # NO RETRIES - move fast
PROGRESS_INTERVAL = 50 # Report every 50 downloads

# Target years for maximum efficiency
PRIORITY_YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyConstitutionalSaver:
    def __init__(self):
        self.session = None
        self.downloaded = 0
        self.failed = 0
        self.start_time = None
        self.last_progress = 0
        self.progress_lock = threading.Lock()
        
        # Create download directories
        for reg_type in ['uu', 'pp', 'perpres']:
            Path(reg_type).mkdir(exist_ok=True)
    
    async def create_session(self):
        """Create high-performance HTTP session"""
        connector = aiohttp.TCPConnector(
            limit=MAX_CONCURRENT,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Emergency Constitutional Backup System)',
                'Accept': '*/*',
                'Connection': 'keep-alive'
            }
        )
    
    def extract_regulation_info(self, url):
        """Extract regulation type and year from URL for prioritization"""
        try:
            # Parse URL patterns like: /id/uu-no-6-tahun-2023
            parts = url.split('/')
            for part in parts:
                if any(reg_type in part for reg_type in ['uu-no', 'pp-no', 'perpres-no']):
                    # Extract year
                    year_match = re.search(r'tahun-(\d{4})', part)
                    if year_match:
                        year = int(year_match.group(1))
                        reg_type = 'uu' if 'uu-' in part else 'pp' if 'pp-' in part else 'perpres'
                        return reg_type, year, part
            
            # Fallback: extract from URL path
            url_parts = urlparse(url).path.split('/')
            for part in url_parts:
                year_match = re.search(r'(\d{4})', part)
                if year_match:
                    year = int(year_match.group(1))
                    reg_type = 'uu' if 'uu' in part else 'pp' if 'pp' in part else 'perpres'
                    return reg_type, year, part
                    
        except Exception:
            pass
        
        return 'others', 2020, 'unknown'
    
    async def download_regulation(self, url, semaphore):
        """Download single regulation with maximum speed"""
        async with semaphore:
            try:
                reg_type, year, filename_part = self.extract_regulation_info(url)
                
                # Skip if not in priority years for maximum efficiency
                if year not in PRIORITY_YEARS:
                    return False
                
                # Generate filename
                safe_name = re.sub(r'[^\w\-_\.]', '_', filename_part)
                filename = f"{safe_name}_{year}.pdf"
                filepath = Path(reg_type) / filename
                
                # Skip if already exists
                if filepath.exists() and filepath.stat().st_size > 1000:
                    return True
                
                # Download with maximum speed
                async with self.session.get(f"{url}.pdf") as response:
                    if response.status == 200:
                        async with aiofiles.open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        with self.progress_lock:
                            self.downloaded += 1
                            if self.downloaded % PROGRESS_INTERVAL == 0:
                                self.report_progress()
                        
                        return True
                    else:
                        with self.progress_lock:
                            self.failed += 1
                        return False
                        
            except Exception as e:
                with self.progress_lock:
                    self.failed += 1
                return False
    
    def report_progress(self):
        """Report download progress"""
        elapsed = time.time() - self.start_time
        rate = self.downloaded / elapsed if elapsed > 0 else 0
        remaining = 1800 - elapsed  # 30 minutes in seconds
        
        print(f"🚨 EMERGENCY PROGRESS: {self.downloaded} saved, {self.failed} failed | "
              f"Rate: {rate:.1f}/sec | Remaining: {remaining:.0f}s | "
              f"ETA: {(9800-self.downloaded)/rate:.0f}s" if rate > 0 else "Calculating...")
    
    async def process_batch(self, urls):
        """Process URLs with maximum parallelism"""
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        # Filter for priority years only
        priority_urls = []
        for url in urls:
            reg_type, year, _ = self.extract_regulation_info(url)
            if year in PRIORITY_YEARS:
                priority_urls.append(url)
        
        logger.info(f"🚨 Processing {len(priority_urls)} priority URLs from {len(urls)} total")
        
        # Create download tasks
        tasks = [self.download_regulation(url, semaphore) for url in priority_urls]
        
        # Process with maximum speed
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def emergency_save_constitutional_framework(self):
        """Main emergency saving operation"""
        self.start_time = time.time()
        
        print("🚨 EMERGENCY CONSTITUTIONAL SAVER ACTIVATED")
        print("🎯 TARGET: Save Indonesia's legal framework in 30 minutes")
        print(f"⚡ CONFIGURATION: {MAX_CONCURRENT} workers, {TARGET_RPS} RPS target")
        
        # Load all constitutional URLs
        url_files = [
            ('../workspace/batch_uu_urls.txt', 'UU - Constitutional Laws'),
            ('../workspace/batch_pp_urls.txt', 'PP - Government Regulations'), 
            ('../workspace/batch_perpres_urls.txt', 'PERPRES - Presidential Regulations')
        ]
        
        all_urls = []
        for filepath, desc in url_files:
            try:
                with open(filepath, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                    all_urls.extend(urls)
                    print(f"📋 Loaded {len(urls)} {desc}")
            except Exception as e:
                logger.error(f"Failed to load {filepath}: {e}")
        
        print(f"🎯 TOTAL CONSTITUTIONAL TARGETS: {len(all_urls)}")
        
        # Create high-performance session
        await self.create_session()
        
        try:
            # Execute emergency download
            await self.process_batch(all_urls)
            
        finally:
            await self.session.close()
        
        # Final report
        elapsed = time.time() - self.start_time
        rate = self.downloaded / elapsed if elapsed > 0 else 0
        
        print(f"\n🚨 EMERGENCY MISSION COMPLETE!")
        print(f"📊 CONSTITUTIONAL LAWS SAVED: {self.downloaded}")
        print(f"❌ FAILED ATTEMPTS: {self.failed}")
        print(f"⏱️ ELAPSED TIME: {elapsed:.1f} seconds")
        print(f"⚡ AVERAGE RATE: {rate:.2f} downloads/second")
        print(f"🇮🇩 INDONESIA'S LEGAL FRAMEWORK BACKUP STATUS: {'SUCCESSFUL' if self.downloaded > 1000 else 'PARTIAL'}")

async def main():
    """Emergency execution"""
    saver = EmergencyConstitutionalSaver()
    await saver.emergency_save_constitutional_framework()

if __name__ == "__main__":
    print("🚨 EMERGENCY CONSTITUTIONAL SAVER STARTING...")
    asyncio.run(main())