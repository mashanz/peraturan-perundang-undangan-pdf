#!/usr/bin/env python3
"""
🚀 SIMPLE TURBO CONSTITUTIONAL DOWNLOADER - 2-HOUR MISSION
ULTRA-FAST APPROACH: Direct threading with minimal overhead
TARGET: 3.6 RPS per agent = 5000+ downloads in 30 minutes
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import signal

class SimpleTurboDownloader:
    def __init__(self):
        self.base_dir = "/root/.openclaw/peraturan-perundang-undangan-pdf"
        self.output_dirs = {
            'uu': os.path.join(self.base_dir, "uu"),
            'pp': os.path.join(self.base_dir, "pp"),
            'perpres': os.path.join(self.base_dir, "perpres")
        }
        
        # TURBO CONFIG
        self.max_workers = 50
        self.request_delay = 0.28  # Slightly faster than 0.33 for turbo
        self.timeout = 20
        
        # Counters (thread-safe)
        self.lock = threading.Lock()
        self.downloads_ok = 0
        self.downloads_failed = 0
        self.downloads_skipped = 0
        self.mission_start = datetime.now()
        
        # Setup
        self.setup_dirs()
        self.setup_logging()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*'
        }
        
        signal.signal(signal.SIGINT, self.shutdown)
        
        print(f"🚀 SIMPLE TURBO DOWNLOADER READY")
        print(f"⚡ Workers: {self.max_workers}, Delay: {self.request_delay}s")
        
    def setup_dirs(self):
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
            
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [TURBO] %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def convert_url(self, web_url):
        """Convert web URL to PDF URL"""
        if '/id/' in web_url:
            reg_id = web_url.split('/id/')[-1].rstrip('/')
            return f"https://peraturan.go.id/files/{reg_id}.pdf"
        return web_url
    
    def download_pdf(self, url, output_dir):
        """Download single PDF"""
        web_url = url.strip()
        pdf_url = self.convert_url(web_url)
        
        # Generate filename
        reg_id = web_url.split('/id/')[-1].rstrip('/')
        filename = f"{reg_id}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Skip if exists and valid
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            with self.lock:
                self.downloads_skipped += 1
                if self.downloads_skipped % 100 == 0:
                    self.quick_report()
            return "SKIP"
        
        try:
            response = requests.get(pdf_url, headers=self.headers, timeout=self.timeout, stream=True)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                
                # Quick validation
                if os.path.getsize(filepath) > 1000:
                    with open(filepath, 'rb') as f:
                        if f.read(4) == b'%PDF':
                            with self.lock:
                                self.downloads_ok += 1
                                if self.downloads_ok % 100 == 0:
                                    self.quick_report()
                            time.sleep(self.request_delay)
                            return "OK"
                
                os.remove(filepath)
                
            with self.lock:
                self.downloads_failed += 1
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            with self.lock:
                self.downloads_failed += 1
        
        time.sleep(self.request_delay)
        return "FAIL"
    
    def quick_report(self):
        """Quick progress report"""
        elapsed = (datetime.now() - self.mission_start).total_seconds() / 60
        total = self.downloads_ok + self.downloads_failed + self.downloads_skipped
        rate = self.downloads_ok / elapsed if elapsed > 0 else 0
        
        print(f"⚡ TURBO: {self.downloads_ok} OK, {self.downloads_failed} FAIL, "
              f"{self.downloads_skipped} SKIP | {rate:.1f}/min | {elapsed:.1f}min")
    
    def load_urls(self):
        """Load all URLs with priority"""
        all_urls = []
        
        batch_files = {
            'uu': '/root/.openclaw/workspace/batch_uu_urls.txt',
            'pp': '/root/.openclaw/workspace/batch_pp_urls.txt', 
            'perpres': '/root/.openclaw/workspace/batch_perpres_urls.txt'
        }
        
        for doc_type, batch_file in batch_files.items():
            if os.path.exists(batch_file):
                with open(batch_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                # Recent years first
                def get_year(url):
                    try:
                        for part in url.split('-'):
                            if part.startswith('tahun-'):
                                return int(part.split('-')[1])
                    except:
                        pass
                    return 2020
                
                urls.sort(key=get_year, reverse=True)
                
                for url in urls:
                    all_urls.append((url, self.output_dirs[doc_type]))
                    
                print(f"📋 Loaded {len(urls)} {doc_type.upper()} URLs")
        
        print(f"📋 TOTAL: {len(all_urls)} URLs")
        return all_urls
    
    def run_turbo(self):
        """Run turbo download"""
        print("🚀 STARTING SIMPLE TURBO MISSION")
        
        urls = self.load_urls()
        if len(urls) > 5000:
            urls = urls[:5000]
            print(f"🎯 Limited to first 5000 URLs for 30-minute target")
        
        print(f"⚡ Starting {self.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.download_pdf, url, output_dir) 
                      for url, output_dir in urls]
            
            # Simple completion tracking
            completed = 0
            for future in futures:
                try:
                    result = future.result()
                    completed += 1
                    if completed % 500 == 0:
                        print(f"⚡ COMPLETED: {completed}/{len(urls)}")
                except Exception as e:
                    completed += 1
        
        self.final_report()
    
    def final_report(self):
        """Final mission report"""
        elapsed = datetime.now() - self.mission_start
        total = self.downloads_ok + self.downloads_failed + self.downloads_skipped
        
        print("\n" + "="*60)
        print("🏆 SIMPLE TURBO MISSION COMPLETE")
        print("="*60)
        print(f"✅ Downloaded: {self.downloads_ok}")
        print(f"❌ Failed: {self.downloads_failed}")
        print(f"⏭️  Skipped: {self.downloads_skipped}")
        print(f"📊 Total: {total}")
        print(f"⏱️  Runtime: {elapsed}")
        
        if self.downloads_ok > 0:
            rate = self.downloads_ok / (elapsed.total_seconds() / 60)
            success = self.downloads_ok / (self.downloads_ok + self.downloads_failed)
            print(f"⚡ Rate: {rate:.1f} downloads/minute")
            print(f"🎯 Success: {success:.1%}")
        
        # Save final results
        results = {
            'downloads_ok': self.downloads_ok,
            'downloads_failed': self.downloads_failed,
            'downloads_skipped': self.downloads_skipped,
            'runtime_minutes': elapsed.total_seconds() / 60,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(os.path.join(self.base_dir, 'simple_turbo_results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        print("="*60)
    
    def shutdown(self, signum, frame):
        print(f"\n⚠️  Shutdown signal {signum}")
        self.final_report()
        sys.exit(0)

def main():
    downloader = SimpleTurboDownloader()
    downloader.run_turbo()

if __name__ == "__main__":
    main()