#!/usr/bin/env python3
"""
AGGRESSIVE CONSTITUTIONAL DOWNLOADER - High-Speed Government Regulation Download
Mission: Download 9,829 constitutional/government documents with server capacity testing
Target: UU, PP, PERPRES - Start at 10 RPS, scale to 50-100 RPS if server handles it

CRITICAL FEATURES:
- Dynamic rate adjustment based on server performance
- Server capacity testing and monitoring
- Aggressive scaling with fallback protection
- Resume capability with progress checkpointing
"""

import os
import sys
import time
import json
import logging
import requests
import threading
from datetime import datetime, timedelta
from collections import deque, defaultdict
from urllib.parse import urlparse
import signal
import statistics

class AggressiveConstitutionalDownloader:
    def __init__(self):
        self.base_dir = "/root/.openclaw/peraturan-perundang-undangan-pdf"
        self.constitutional_dir = os.path.join(self.base_dir, "constitutional")
        self.pp_dir = os.path.join(self.base_dir, "pp") 
        self.perpres_dir = os.path.join(self.base_dir, "perpres")
        self.uu_dir = os.path.join(self.base_dir, "uu")
        
        # Aggressive rate configuration
        self.current_rps = 10  # Start at 10 requests/second
        self.min_rps = 1       # Fallback minimum
        self.max_rps = 100     # Maximum target
        self.scale_test_rps = [10, 15, 25, 40, 50, 75, 100]  # Scaling test points
        self.current_delay = 0.1  # Start with 0.1s delay (10 RPS)
        
        # Server monitoring
        self.response_times = deque(maxlen=50)  # Track last 50 response times
        self.status_codes = deque(maxlen=100)   # Track last 100 status codes  
        self.error_count = 0
        self.consecutive_successes = 0
        self.consecutive_errors = 0
        self.rate_limit_detected = False
        
        # Progress tracking
        self.total_downloaded = 0
        self.total_failed = 0
        self.total_skipped = 0
        self.session_start = datetime.now()
        self.last_checkpoint = datetime.now()
        
        # Performance metrics
        self.performance_log = []
        self.current_test_phase = "INITIAL_10RPS"
        
        # File paths
        self.batch_files = {
            'uu': '/root/.openclaw/workspace/batch_uu_urls.txt',
            'pp': '/root/.openclaw/workspace/batch_pp_urls.txt', 
            'perpres': '/root/.openclaw/workspace/batch_perpres_urls.txt'
        }
        
        self.progress_file = os.path.join(self.base_dir, "aggressive_constitutional_progress.json")
        self.performance_file = os.path.join(self.base_dir, "server_performance_log.json")
        self.log_file = os.path.join(self.base_dir, "aggressive_constitutional.log")
        
        # Setup
        self.setup_logging()
        self.setup_directories()
        self.load_progress()
        
        # Request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'id,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://peraturan.go.id/'
        }
        
        # Shutdown handler
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        
        self.logger.info("=== AGGRESSIVE CONSTITUTIONAL DOWNLOADER INITIALIZED ===")
        self.logger.info(f"Target documents: 9,829 constitutional/government regulations")
        self.logger.info(f"Starting RPS: {self.current_rps} (delay: {self.current_delay}s)")
        self.logger.info(f"Maximum target RPS: {self.max_rps}")
        self.logger.info("SERVER CAPACITY TESTING ENABLED - Will scale aggressively")
    
    def setup_logging(self):
        """Setup comprehensive logging with performance metrics"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        """Create output directories"""
        for dir_path in [self.constitutional_dir, self.pp_dir, self.perpres_dir, self.uu_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def load_progress(self):
        """Load previous progress checkpoint"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
                self.total_downloaded = progress.get('total_downloaded', 0)
                self.total_failed = progress.get('total_failed', 0) 
                self.total_skipped = progress.get('total_skipped', 0)
                self.logger.info(f"RESUMING: Downloaded={self.total_downloaded}, Failed={self.total_failed}, Skipped={self.total_skipped}")
    
    def save_progress(self):
        """Save progress checkpoint"""
        progress = {
            'total_downloaded': self.total_downloaded,
            'total_failed': self.total_failed,
            'total_skipped': self.total_skipped,
            'current_rps': self.current_rps,
            'current_delay': self.current_delay,
            'test_phase': self.current_test_phase,
            'timestamp': datetime.now().isoformat(),
            'runtime_minutes': (datetime.now() - self.session_start).total_seconds() / 60
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def log_performance_metrics(self, response_time, status_code, url):
        """Log detailed performance metrics for server monitoring"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'response_time': response_time,
            'status_code': status_code,
            'rps': self.current_rps,
            'delay': self.current_delay,
            'phase': self.current_test_phase,
            'consecutive_successes': self.consecutive_successes,
            'consecutive_errors': self.consecutive_errors,
            'url': url
        }
        
        self.performance_log.append(metric)
        
        # Save performance log every 100 requests
        if len(self.performance_log) % 100 == 0:
            with open(self.performance_file, 'w') as f:
                json.dump(self.performance_log, f, indent=2)
    
    def analyze_server_performance(self):
        """Analyze recent server performance and adjust rate accordingly"""
        if len(self.response_times) < 10:
            return  # Need more data
        
        avg_response_time = statistics.mean(self.response_times)
        recent_status_codes = list(self.status_codes)[-20:]  # Last 20 requests
        error_rate = sum(1 for code in recent_status_codes if code >= 400) / len(recent_status_codes)
        
        # Check for rate limiting indicators
        rate_limit_codes = [429, 503, 504, 502, 500]
        recent_rate_limits = sum(1 for code in recent_status_codes if code in rate_limit_codes)
        
        self.logger.info(f"PERFORMANCE ANALYSIS - RPS: {self.current_rps}, "
                        f"Avg Response: {avg_response_time:.3f}s, Error Rate: {error_rate:.2%}, "
                        f"Rate Limits: {recent_rate_limits}")
        
        # Aggressive scaling logic
        if error_rate > 0.1:  # >10% error rate
            self.scale_down("High error rate detected")
        elif recent_rate_limits > 2:  # Multiple rate limit responses
            self.scale_down("Rate limiting detected")
            self.rate_limit_detected = True
        elif avg_response_time > 5.0:  # >5s response time
            self.scale_down("Slow server response")
        elif self.consecutive_successes > 100 and error_rate < 0.02:  # <2% error rate, many successes
            if not self.rate_limit_detected:
                self.scale_up("Server performing well")
        
    def scale_up(self, reason):
        """Aggressively scale up RPS if server can handle it"""
        if self.current_rps >= self.max_rps:
            return
        
        # Find next test point
        next_rps = None
        for test_rps in self.scale_test_rps:
            if test_rps > self.current_rps:
                next_rps = test_rps
                break
        
        if next_rps and next_rps <= self.max_rps:
            old_rps = self.current_rps
            self.current_rps = next_rps
            self.current_delay = 1.0 / self.current_rps
            self.current_test_phase = f"SCALING_{next_rps}RPS"
            
            self.logger.warning(f"🚀 SCALING UP: {old_rps} → {next_rps} RPS (delay: {self.current_delay:.3f}s) - {reason}")
            
            # Reset monitoring counters for new rate
            self.consecutive_successes = 0
            self.consecutive_errors = 0
    
    def scale_down(self, reason):
        """Scale down RPS when server shows stress"""
        if self.current_rps <= self.min_rps:
            return
        
        # Find previous safe RPS level
        new_rps = max(self.min_rps, self.current_rps // 2)  # Halve the rate
        old_rps = self.current_rps
        
        self.current_rps = new_rps
        self.current_delay = 1.0 / self.current_rps
        self.current_test_phase = f"FALLBACK_{new_rps}RPS"
        
        self.logger.warning(f"⚠️  SCALING DOWN: {old_rps} → {new_rps} RPS (delay: {self.current_delay:.3f}s) - {reason}")
        
        # Reset monitoring counters
        self.consecutive_successes = 0
        self.consecutive_errors = 0
        
        # Clear rate limit flag after scaling down
        if self.rate_limit_detected:
            time.sleep(5)  # Brief pause after rate limiting
            self.rate_limit_detected = False
    
    def convert_to_pdf_url(self, web_url):
        """Convert peraturan.go.id webpage URL to direct PDF URL"""
        # Extract regulation ID from URL like https://peraturan.go.id/id/uu-no-6-tahun-2023
        if '/id/' in web_url:
            reg_id = web_url.split('/id/')[-1].rstrip('/')
            return f"https://peraturan.go.id/files/{reg_id}.pdf"
        return web_url
    
    def download_pdf(self, url, target_dir, doc_type):
        """Download single PDF with performance monitoring"""
        web_url = url.strip()
        pdf_url = self.convert_to_pdf_url(web_url)
        
        # Generate filename
        reg_id = web_url.split('/id/')[-1].rstrip('/')
        filename = f"{reg_id}.pdf"
        filepath = os.path.join(target_dir, filename)
        
        # Skip if already exists
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:  # >1KB
            self.total_skipped += 1
            return True
        
        # Download with timing
        start_time = time.time()
        try:
            response = requests.get(pdf_url, headers=self.headers, timeout=15, stream=True)
            response_time = time.time() - start_time
            
            # Log performance metrics
            self.response_times.append(response_time)
            self.status_codes.append(response.status_code)
            self.log_performance_metrics(response_time, response.status_code, pdf_url)
            
            if response.status_code == 200:
                # Save PDF
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Verify PDF integrity
                if os.path.getsize(filepath) > 1000:  # Basic size check
                    with open(filepath, 'rb') as f:
                        if f.read(4) == b'%PDF':  # PDF header check
                            self.total_downloaded += 1
                            self.consecutive_successes += 1
                            self.consecutive_errors = 0
                            
                            # Progress reporting
                            if self.total_downloaded % 50 == 0:
                                self.report_progress()
                            
                            return True
                
                # Remove invalid file
                os.remove(filepath)
                self.logger.warning(f"Invalid PDF removed: {filename}")
            
            # Handle error status codes
            self.consecutive_errors += 1
            self.consecutive_successes = 0
            self.total_failed += 1
            
            if response.status_code in [429, 503, 504]:
                self.logger.warning(f"Rate limit/server error {response.status_code}: {filename}")
                time.sleep(2)  # Brief pause for rate limiting
            else:
                self.logger.warning(f"HTTP {response.status_code}: {filename}")
            
        except Exception as e:
            self.consecutive_errors += 1
            self.consecutive_successes = 0 
            self.total_failed += 1
            self.logger.error(f"Download failed {filename}: {e}")
        
        return False
    
    def process_batch_file(self, batch_file, target_dir, doc_type, limit=None):
        """Process URLs from batch file with aggressive rate testing"""
        if not os.path.exists(batch_file):
            self.logger.error(f"Batch file not found: {batch_file}")
            return
        
        self.logger.info(f"🎯 PROCESSING {doc_type.upper()} DOCUMENTS")
        self.logger.info(f"Batch file: {batch_file}")
        self.logger.info(f"Target directory: {target_dir}")
        
        with open(batch_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if limit:
            urls = urls[:limit]
        
        self.logger.info(f"Processing {len(urls)} {doc_type} URLs with aggressive scaling")
        
        batch_start = datetime.now()
        batch_downloaded = 0
        
        for i, url in enumerate(urls, 1):
            # Download PDF
            if self.download_pdf(url, target_dir, doc_type):
                batch_downloaded += 1
            
            # Rate limiting with dynamic adjustment
            time.sleep(self.current_delay)
            
            # Performance analysis every 25 downloads
            if i % 25 == 0:
                self.analyze_server_performance()
                self.save_progress()
            
            # Major progress report every 250 downloads
            if i % 250 == 0:
                elapsed = datetime.now() - batch_start
                rate = batch_downloaded / elapsed.total_seconds()
                self.logger.info(f"📊 BATCH PROGRESS [{doc_type.upper()}]: {i}/{len(urls)} "
                               f"({i/len(urls):.1%}) - Downloaded: {batch_downloaded}, "
                               f"Current rate: {rate:.2f} files/sec")
        
        # Batch completion report
        elapsed = datetime.now() - batch_start
        self.logger.info(f"✅ {doc_type.upper()} BATCH COMPLETE: {batch_downloaded} files in {elapsed}")
    
    def report_progress(self):
        """Report detailed progress with performance metrics"""
        elapsed = datetime.now() - self.session_start
        total_processed = self.total_downloaded + self.total_failed + self.total_skipped
        
        if total_processed > 0:
            success_rate = self.total_downloaded / (self.total_downloaded + self.total_failed)
            files_per_minute = self.total_downloaded / (elapsed.total_seconds() / 60)
            
            self.logger.info(f"📈 PROGRESS REPORT - Phase: {self.current_test_phase}")
            self.logger.info(f"   Downloaded: {self.total_downloaded}, Failed: {self.total_failed}, Skipped: {self.total_skipped}")
            self.logger.info(f"   Success Rate: {success_rate:.2%}, Speed: {files_per_minute:.1f} files/min")
            self.logger.info(f"   Current RPS: {self.current_rps}, Delay: {self.current_delay:.3f}s")
            self.logger.info(f"   Runtime: {elapsed}")
            
            if len(self.response_times) > 0:
                avg_response = statistics.mean(self.response_times)
                self.logger.info(f"   Avg Response Time: {avg_response:.3f}s")
    
    def run_aggressive_download(self):
        """Run the complete aggressive download operation"""
        self.logger.info("🚀 STARTING AGGRESSIVE CONSTITUTIONAL DOWNLOAD")
        self.logger.info("STRATEGY: Start 10 RPS → Scale to 50-100 RPS based on server capacity")
        
        # Priority order: UU → PP → PERPRES
        batch_configs = [
            ('uu', self.uu_dir, 'Constitutional Laws', None),  # All UU documents
            ('pp', self.pp_dir, 'Government Regulations', 2000),  # First 2000 PP
            ('perpres', self.perpres_dir, 'Presidential Regulations', 1000)  # First 1000 PERPRES
        ]
        
        total_target = 9829
        total_processed = 0
        
        for doc_type, target_dir, description, limit in batch_configs:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🎯 STARTING {description.upper()} DOWNLOAD")
            self.logger.info(f"Type: {doc_type}, Limit: {limit or 'ALL'}")
            self.logger.info(f"{'='*60}")
            
            batch_file = self.batch_files[doc_type]
            self.process_batch_file(batch_file, target_dir, doc_type, limit)
            
            # Brief pause between batches
            self.logger.info(f"Completed {doc_type.upper()}. Pausing 10 seconds before next batch...")
            time.sleep(10)
        
        # Final mission report
        self.final_report()
    
    def final_report(self):
        """Generate comprehensive mission completion report"""
        total_runtime = datetime.now() - self.session_start
        total_processed = self.total_downloaded + self.total_failed + self.total_skipped
        
        self.logger.info("\n" + "="*80)
        self.logger.info("🏆 AGGRESSIVE CONSTITUTIONAL DOWNLOAD MISSION COMPLETE")
        self.logger.info("="*80)
        self.logger.info(f"📊 FINAL STATISTICS:")
        self.logger.info(f"   Total Downloaded: {self.total_downloaded}")
        self.logger.info(f"   Total Failed: {self.total_failed}")
        self.logger.info(f"   Total Skipped: {self.total_skipped}")
        self.logger.info(f"   Total Processed: {total_processed}")
        self.logger.info(f"   Success Rate: {self.total_downloaded/(self.total_downloaded + self.total_failed):.2%}")
        self.logger.info(f"   Runtime: {total_runtime}")
        
        if self.total_downloaded > 0:
            files_per_minute = self.total_downloaded / (total_runtime.total_seconds() / 60)
            self.logger.info(f"   Average Speed: {files_per_minute:.1f} files/minute")
        
        # Server performance summary
        if len(self.performance_log) > 0:
            avg_rps = statistics.mean([p['rps'] for p in self.performance_log])
            max_rps = max([p['rps'] for p in self.performance_log])
            self.logger.info(f"🚀 SERVER CAPACITY RESULTS:")
            self.logger.info(f"   Average RPS Achieved: {avg_rps:.1f}")
            self.logger.info(f"   Maximum RPS Reached: {max_rps}")
            self.logger.info(f"   Final RPS: {self.current_rps}")
        
        # Save final progress
        self.save_progress()
        
        self.logger.info("="*80)
        self.logger.info("Mission Status: SUCCESS - Aggressive download operation completed!")
    
    def graceful_shutdown(self, signum, frame):
        """Handle graceful shutdown on signal"""
        self.logger.info(f"\n⚠️  Received shutdown signal {signum}")
        self.logger.info("Saving progress and shutting down gracefully...")
        self.save_progress()
        self.final_report()
        sys.exit(0)

def main():
    downloader = AggressiveConstitutionalDownloader()
    downloader.run_aggressive_download()

if __name__ == "__main__":
    main()