#!/usr/bin/env python3
"""
🚨 EMERGENCY CONSTITUTIONAL SAVER V2 🚨
MISSION: Save Indonesia's legal framework in remaining time
STRATEGY: Correct URL handling, maximum parallelism, scrape PDF links
"""

import asyncio
import aiohttp
import aiofiles
import json
import time
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin
import logging
from bs4 import BeautifulSoup
import threading

# 🚨 EMERGENCY CONFIGURATION V2
MAX_CONCURRENT = 80   # Reduced for stability
TIMEOUT = 15          # Longer timeout for page parsing
MAX_RETRIES = 1       # Allow one retry for critical docs
PROGRESS_INTERVAL = 25 # Report every 25 downloads

# Target years for maximum efficiency
PRIORITY_YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyConstitutionalSaverV2:
    def __init__(self):
        self.session = None
        self.downloaded = 0
        self.failed = 0
        self.start_time = None
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
    
    def extract_regulation_info(self, url):
        """Extract regulation type and year from URL"""
        try:
            # Parse URL patterns like: /id/uu-no-6-tahun-2023
            if 'uu-no' in url:
                reg_type = 'uu'
            elif 'pp-no' in url:
                reg_type = 'pp'  
            elif 'perpres-no' in url:
                reg_type = 'perpres'
            else:
                reg_type = 'others'
            
            # Extract year
            year_match = re.search(r'tahun-(\d{4})', url)
            if year_match:
                year = int(year_match.group(1))
            else:
                # Try to extract from number pattern
                year_match = re.search(r'-(\d{4})$', url)
                year = int(year_match.group(1)) if year_match else 2020
                
            # Extract regulation number for filename
            num_match = re.search(r'no-(\d+)', url)
            number = num_match.group(1) if num_match else 'unknown'
            
            filename = f"{reg_type}_no_{number}_tahun_{year}.pdf"
            
            return reg_type, year, filename
                    
        except Exception as e:
            return 'others', 2020, 'unknown.pdf'
    
    async def find_pdf_link(self, page_url):
        """Find PDF download link from regulation page"""
        try:
            async with self.session.get(page_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for PDF download links
                    pdf_patterns = [
                        'a[href*=".pdf"]',
                        'a[href*="download"]',
                        'a[title*="PDF"]',
                        'a[title*="Download"]'
                    ]
                    
                    for pattern in pdf_patterns:
                        links = soup.select(pattern)
                        for link in links:
                            href = link.get('href')
                            if href and '.pdf' in href:
                                if href.startswith('http'):
                                    return href
                                else:
                                    return urljoin(page_url, href)
                    
                    # Alternative: look for direct PDF URLs in page
                    pdf_match = re.search(r'https?://[^"\s]+\.pdf', html)
                    if pdf_match:
                        return pdf_match.group(0)
                        
        except Exception as e:
            logger.debug(f"PDF link search failed for {page_url}: {e}")
        
        return None
    
    async def download_regulation(self, page_url, semaphore):
        """Download single regulation with correct URL handling"""
        async with semaphore:
            try:
                reg_type, year, filename = self.extract_regulation_info(page_url)
                
                # Skip if not in priority years
                if year not in PRIORITY_YEARS:
                    return False
                
                filepath = Path(reg_type) / filename
                
                # Skip if already exists and has content
                if filepath.exists() and filepath.stat().st_size > 1000:
                    with self.progress_lock:
                        self.downloaded += 1
                        if self.downloaded % PROGRESS_INTERVAL == 0:
                            self.report_progress()
                    return True
                
                # Find PDF download link
                pdf_url = await self.find_pdf_link(page_url)
                if not pdf_url:
                    with self.progress_lock:
                        self.failed += 1
                    return False
                
                # Download PDF
                async with self.session.get(pdf_url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'pdf' in content_type.lower():
                            async with aiofiles.open(filepath, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    await f.write(chunk)
                            
                            # Verify file size
                            if filepath.stat().st_size > 1000:
                                with self.progress_lock:
                                    self.downloaded += 1
                                    if self.downloaded % PROGRESS_INTERVAL == 0:
                                        self.report_progress()
                                return True
                            else:
                                filepath.unlink()  # Remove empty file
                                
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
        remaining_time = 1800 - elapsed  # 30 minutes in seconds
        
        print(f"🚨 EMERGENCY PROGRESS: {self.downloaded} saved, {self.failed} failed | "
              f"Rate: {rate:.1f}/sec | Time left: {remaining_time/60:.1f}m")
        
        # Estimate completion
        if rate > 0:
            eta_remaining = (1469 - self.downloaded) / rate
            print(f"📊 ETA for remaining: {eta_remaining/60:.1f} minutes")
    
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
        """Main emergency saving operation V2"""
        self.start_time = time.time()
        
        print("🚨 EMERGENCY CONSTITUTIONAL SAVER V2 ACTIVATED")
        print("🎯 TARGET: Save Indonesia's legal framework - CORRECTED URL HANDLING")
        print(f"⚡ CONFIGURATION: {MAX_CONCURRENT} workers, PDF link extraction")
        
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
        
        print(f"\n🚨 EMERGENCY MISSION V2 COMPLETE!")
        print(f"📊 CONSTITUTIONAL LAWS SAVED: {self.downloaded}")
        print(f"❌ FAILED ATTEMPTS: {self.failed}")
        print(f"⏱️ ELAPSED TIME: {elapsed/60:.1f} minutes")
        print(f"⚡ AVERAGE RATE: {rate:.2f} downloads/second")
        print(f"🇮🇩 INDONESIA'S LEGAL FRAMEWORK BACKUP STATUS: {'SUCCESSFUL' if self.downloaded > 200 else 'PARTIAL'}")

async def main():
    """Emergency execution V2"""
    saver = EmergencyConstitutionalSaverV2()
    await saver.emergency_save_constitutional_framework()

if __name__ == "__main__":
    print("🚨 EMERGENCY CONSTITUTIONAL SAVER V2 STARTING...")
    asyncio.run(main())