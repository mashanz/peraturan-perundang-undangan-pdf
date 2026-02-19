#!/usr/bin/env python3
"""
FOCUSED AGGRESSIVE DOWNLOADER - High-Speed Constitutional Download (Recent Documents)
Optimized for server capacity testing with documents that actually have PDF versions
Focus: Recent UU (1980+), PP, PERPRES with aggressive RPS scaling
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
import statistics
from collections import deque
import threading
import signal

class FocusedAggressiveDownloader:
    def __init__(self):
        self.base_dir = "/root/.openclaw/peraturan-perundang-undangan-pdf"
        
        # Aggressive scaling parameters
        self.current_rps = 15  # Start higher since we know these work
        self.current_delay = 1.0 / self.current_rps
        self.rps_levels = [15, 25, 40, 60, 80, 100]  # Aggressive scaling
        self.max_rps = 100
        self.min_rps = 5
        
        # Performance monitoring
        self.response_times = deque(maxlen=30)
        self.status_codes = deque(maxlen=50)
        self.consecutive_successes = 0
        self.consecutive_errors = 0
        
        # Counters
        self.downloaded = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = datetime.now()
        
        # Setup
        self.setup_logging()
        self.setup_directories()
        
        # Headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*',
            'Connection': 'keep-alive'
        }
        
        self.logger.info("🚀 FOCUSED AGGRESSIVE DOWNLOADER - Recent Documents Only")
        self.logger.info(f"Starting RPS: {self.current_rps} (targeting recent documents with PDF versions)")
    
    def setup_logging(self):
        log_file = os.path.join(self.base_dir, "focused_aggressive.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        for dir_name in ['uu', 'pp', 'perpres']:
            os.makedirs(os.path.join(self.base_dir, dir_name), exist_ok=True)
    
    def analyze_performance(self):
        """Analyze server performance and scale RPS aggressively"""
        if len(self.response_times) < 10:
            return
        
        avg_response = statistics.mean(self.response_times)
        recent_codes = list(self.status_codes)[-20:]
        error_rate = sum(1 for code in recent_codes if code >= 400) / len(recent_codes)
        
        self.logger.info(f"📊 PERF: RPS={self.current_rps}, Response={avg_response:.2f}s, "
                        f"Success={self.consecutive_successes}, Errors={error_rate:.1%}")
        
        # Aggressive scaling logic
        if error_rate > 0.15:  # >15% errors
            self.scale_down("High error rate")
        elif any(code in [429, 503, 504] for code in recent_codes[-5:]):
            self.scale_down("Rate limiting detected")
        elif avg_response > 8.0:  # Very slow responses
            self.scale_down("Server overloaded")
        elif (self.consecutive_successes >= 50 and error_rate < 0.05 and 
              avg_response < 3.0):  # Excellent performance
            self.scale_up("Server handling load well")
    
    def scale_up(self, reason):
        """Scale up to next RPS level"""
        current_index = -1
        for i, rps in enumerate(self.rps_levels):
            if rps == self.current_rps:
                current_index = i
                break
        
        if current_index >= 0 and current_index < len(self.rps_levels) - 1:
            new_rps = self.rps_levels[current_index + 1]
            self.current_rps = new_rps
            self.current_delay = 1.0 / new_rps
            self.consecutive_successes = 0
            self.logger.warning(f"⬆️  SCALING UP to {new_rps} RPS - {reason}")
    
    def scale_down(self, reason):
        """Scale down to previous RPS level"""
        current_index = -1
        for i, rps in enumerate(self.rps_levels):
            if rps == self.current_rps:
                current_index = i
                break
        
        if current_index > 0:
            new_rps = self.rps_levels[current_index - 1]
            self.current_rps = new_rps
            self.current_delay = 1.0 / new_rps
            self.consecutive_errors = 0
            self.logger.warning(f"⬇️  SCALING DOWN to {new_rps} RPS - {reason}")
            time.sleep(2)  # Brief pause after scaling down
    
    def download_pdf(self, url, target_dir):
        """Download single PDF with performance tracking"""
        reg_id = url.split('/id/')[-1].strip()
        pdf_url = f"https://peraturan.go.id/files/{reg_id}.pdf"
        filename = f"{reg_id}.pdf"
        filepath = os.path.join(target_dir, filename)
        
        # Skip if exists
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            self.skipped += 1
            return True
        
        start_time = time.time()
        try:
            response = requests.get(pdf_url, headers=self.headers, timeout=10, stream=True)
            response_time = time.time() - start_time
            
            # Track performance
            self.response_times.append(response_time)
            self.status_codes.append(response.status_code)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Verify PDF
                if os.path.getsize(filepath) > 1000:
                    with open(filepath, 'rb') as f:
                        if f.read(4) == b'%PDF':
                            self.downloaded += 1
                            self.consecutive_successes += 1
                            self.consecutive_errors = 0
                            return True
                
                # Remove invalid file
                os.remove(filepath)
            
            self.failed += 1
            self.consecutive_errors += 1
            self.consecutive_successes = 0
            
        except Exception as e:
            self.failed += 1
            self.consecutive_errors += 1
            self.consecutive_successes = 0
            if "timeout" not in str(e).lower():
                self.logger.warning(f"Error downloading {filename}: {e}")
        
        return False
    
    def process_url_file(self, url_file, target_dir, doc_type, limit=None):
        """Process URLs from file with aggressive rate scaling"""
        if not os.path.exists(url_file):
            self.logger.error(f"URL file not found: {url_file}")
            return
        
        with open(url_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if limit:
            urls = urls[:limit]
        
        self.logger.info(f"🎯 PROCESSING {len(urls)} {doc_type.upper()} URLs")
        self.logger.info(f"Target: Maximum server capacity with {doc_type} documents")
        
        start_batch = datetime.now()
        
        for i, url in enumerate(urls, 1):
            self.download_pdf(url, target_dir)
            
            # Progress reports
            if i % 25 == 0:
                self.analyze_performance()
                self.report_progress(i, len(urls), doc_type, start_batch)
            
            # Aggressive rate control
            time.sleep(self.current_delay)
        
        self.logger.info(f"✅ {doc_type.upper()} BATCH COMPLETE")
    
    def report_progress(self, current, total, doc_type, start_time):
        """Report detailed progress"""
        elapsed = datetime.now() - start_time
        percent = (current / total) * 100
        rate = self.downloaded / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        
        self.logger.info(f"📈 PROGRESS [{doc_type}]: {current}/{total} ({percent:.1f}%) | "
                        f"Downloaded: {self.downloaded} | Failed: {self.failed} | "
                        f"Rate: {rate:.1f}/sec | RPS: {self.current_rps}")
    
    def run_focused_mission(self):
        """Run the focused aggressive download mission"""
        self.logger.info("🚀 STARTING FOCUSED AGGRESSIVE DOWNLOAD MISSION")
        self.logger.info("STRATEGY: Recent documents (1980+) → Scale 15-100 RPS → Maximum server capacity")
        
        # Process recent UU documents first (most likely to succeed)
        recent_uu_file = os.path.join(self.base_dir, "recent_uu_urls.txt")
        uu_dir = os.path.join(self.base_dir, "uu")
        
        self.process_url_file(recent_uu_file, uu_dir, "UU", limit=500)  # First 500 recent UU
        
        # Brief pause, then process PP documents
        self.logger.info("Pausing 5 seconds before PP batch...")
        time.sleep(5)
        
        pp_file = "/root/.openclaw/workspace/batch_pp_urls.txt"
        pp_dir = os.path.join(self.base_dir, "pp")
        
        # Filter recent PP documents on the fly
        self.process_recent_documents(pp_file, pp_dir, "PP", 1000)
        
        # Final report
        self.final_report()
    
    def process_recent_documents(self, source_file, target_dir, doc_type, limit):
        """Process only recent documents from source file"""
        if not os.path.exists(source_file):
            return
        
        self.logger.info(f"🎯 PROCESSING RECENT {doc_type} DOCUMENTS (filtering on-the-fly)")
        
        recent_urls = []
        with open(source_file, 'r') as f:
            for line in f:
                url = line.strip()
                # Filter for recent documents (1990+)
                if any(year in url for year in [f'tahun-{y}' for y in range(1990, 2027)]):
                    recent_urls.append(url)
                    if len(recent_urls) >= limit:
                        break
        
        self.logger.info(f"Found {len(recent_urls)} recent {doc_type} documents")
        
        start_batch = datetime.now()
        for i, url in enumerate(recent_urls, 1):
            self.download_pdf(url, target_dir)
            
            if i % 25 == 0:
                self.analyze_performance()
                self.report_progress(i, len(recent_urls), doc_type, start_batch)
            
            time.sleep(self.current_delay)
    
    def final_report(self):
        """Generate mission completion report"""
        total_time = datetime.now() - self.start_time
        total_processed = self.downloaded + self.failed + self.skipped
        
        self.logger.info("\n" + "="*70)
        self.logger.info("🏆 FOCUSED AGGRESSIVE DOWNLOAD MISSION COMPLETE")
        self.logger.info("="*70)
        self.logger.info(f"📊 FINAL RESULTS:")
        self.logger.info(f"   Downloaded: {self.downloaded}")
        self.logger.info(f"   Failed: {self.failed}")
        self.logger.info(f"   Skipped: {self.skipped}")
        self.logger.info(f"   Total Processed: {total_processed}")
        
        if self.downloaded + self.failed > 0:
            success_rate = self.downloaded / (self.downloaded + self.failed)
            self.logger.info(f"   Success Rate: {success_rate:.1%}")
        
        if total_time.total_seconds() > 0:
            rate = self.downloaded / total_time.total_seconds()
            self.logger.info(f"   Average Speed: {rate:.2f} files/sec")
        
        self.logger.info(f"   Final RPS: {self.current_rps}")
        self.logger.info(f"   Runtime: {total_time}")
        self.logger.info("="*70)

def main():
    downloader = FocusedAggressiveDownloader()
    downloader.run_focused_mission()

if __name__ == "__main__":
    main()