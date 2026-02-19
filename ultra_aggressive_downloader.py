#!/usr/bin/env python3
"""
ULTRA AGGRESSIVE PERMEN MASS DOWNLOADER
MISSION: Extreme RPS testing with parallel ministry processing
TARGET: 25 RPS → 100+ RPS with server capacity testing

PRIORITY MINISTRIES:
1. Finance (kemenkeu): 3,839 regulations
2. Trade (kemendag): 2,234 regulations  
3. Transportation (kemenhub): 1,247 regulations
4. Education (kemdikbud): 916 regulations
5. Health (kemkes): 871 regulations
"""

import os
import sys
import time
import json
import logging
import requests
import threading
import multiprocessing
from queue import Queue, Empty
from urllib.parse import urlparse
import hashlib
import signal
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import random

class UltraAggressiveDownloader:
    def __init__(self, base_dir="/root/.openclaw/peraturan-perundang-undangan-pdf"):
        self.base_dir = base_dir
        self.permen_dir = os.path.join(base_dir, "permen")
        self.batch_dir = os.path.join(base_dir, "permen_batches")
        
        # ULTRA AGGRESSIVE SETTINGS
        self.initial_rps = 25  # Start at 25 requests per second
        self.current_delay = 1.0 / self.initial_rps  # 0.04 seconds
        self.target_rps = 100  # Target 100+ RPS
        self.max_workers = 50  # Maximum concurrent workers
        self.concurrent_ministry_streams = 5  # Parallel ministry processing
        
        # ESCALATION SCHEDULE
        self.escalation_intervals = [
            (300, 25),   # 5 minutes: 25 RPS (0.04s delay)
            (600, 50),   # 10 minutes: 50 RPS (0.02s delay) 
            (900, 75),   # 15 minutes: 75 RPS (0.013s delay)
            (1200, 100), # 20 minutes: 100 RPS (0.01s delay)
            (1800, 150), # 30 minutes: 150 RPS (0.0067s delay)
        ]
        
        # PRIORITY MINISTRY TARGETING
        self.priority_ministries = [
            'kemenkeu',    # Finance: 3,839
            'kemendag',    # Trade: 2,234
            'kemenhub',    # Transportation: 1,247
            'kemdikbud',   # Education: 916
            'kemkes',      # Health: 871
        ]
        
        # Performance monitoring
        self.performance_metrics = {
            'start_time': datetime.now(),
            'total_requests': 0,
            'successful_downloads': 0,
            'failed_requests': 0,
            'current_rps': self.initial_rps,
            'server_errors': [],
            'response_times': [],
            'bandwidth_usage': 0,
            'concurrent_connections': 0,
            'max_concurrent': 0,
        }
        
        # Server stress indicators
        self.stress_indicators = {
            'http_429_count': 0,
            'http_503_count': 0,
            'timeout_count': 0,
            'slow_response_count': 0,  # >5 seconds
            'connection_reset_count': 0,
        }
        
        # Create directories
        os.makedirs(self.permen_dir, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.shutdown_flag = threading.Event()
        
    def setup_logging(self):
        """Setup ultra-aggressive logging"""
        log_file = os.path.join(self.base_dir, "ultra_aggressive_download.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def signal_handler(self, signum, frame):
        """Handle graceful shutdown"""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.shutdown_flag.set()
        self.save_performance_report()
        
    def convert_to_pdf_url(self, webpage_url):
        """Convert peraturan.go.id webpage URL to direct PDF download URL"""
        # Pattern: https://peraturan.go.id/id/regulation-name -> https://peraturan.go.id/files/regulation-name.pdf
        if '/id/' in webpage_url:
            regulation_name = webpage_url.split('/id/')[-1]
            return f"https://peraturan.go.id/files/{regulation_name}.pdf"
        return None  # Invalid format
    
    def classify_ministry(self, url):
        """Classify regulation by ministry from URL patterns"""
        url_lower = url.lower()
        
        # Priority ministries first
        if 'kemenkeu' in url_lower or 'pmk-' in url_lower:
            return 'kemenkeu'
        elif 'kemendag' in url_lower:
            return 'kemendag'
        elif 'kemenhub' in url_lower:
            return 'kemenhub'
        elif 'kemdikbud' in url_lower:
            return 'kemdikbud'
        elif 'kemkes' in url_lower:
            return 'kemkes'
        elif 'esdm' in url_lower:
            return 'esdm'
        elif 'kkp' in url_lower:
            return 'kkp'
        elif 'kementan' in url_lower:
            return 'kementan'
        else:
            return 'unknown'
    
    def get_filename_from_url(self, url, ministry):
        """Generate filename from URL"""
        # Extract document ID or use URL hash
        match = re.search(r'/dokumen/([^/?]+)', url)
        if match:
            doc_id = match.group(1)
            return f"{doc_id}.pdf"
        else:
            # Fallback to URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            return f"{ministry}_{url_hash}.pdf"
    
    def download_single_file(self, url, session=None):
        """Download a single file with aggressive timing"""
        start_time = time.time()
        
        try:
            if session is None:
                session = requests.Session()
                
            # Convert to PDF URL
            pdf_url = self.convert_to_pdf_url(url)
            if not pdf_url:
                self.logger.error(f"Failed to convert URL to PDF: {url}")
                return False, "URL_CONVERSION_FAILED"
            
            # Classify ministry
            ministry = self.classify_ministry(url)
            
            # Generate filename
            filename = self.get_filename_from_url(url, ministry)
            
            # Create ministry directory
            ministry_dir = os.path.join(self.permen_dir, ministry)
            os.makedirs(ministry_dir, exist_ok=True)
            
            # Full file path
            file_path = os.path.join(ministry_dir, filename)
            
            # Skip if file already exists and is valid
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
                return True, "ALREADY_EXISTS"
            
            # Make request with aggressive timeout
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = session.get(
                pdf_url, 
                headers=headers, 
                timeout=10,  # Aggressive timeout
                stream=True
            )
            
            response_time = time.time() - start_time
            self.performance_metrics['response_times'].append(response_time)
            
            # Check for server stress indicators
            if response.status_code == 429:
                self.stress_indicators['http_429_count'] += 1
                return False, "HTTP_429_TOO_MANY_REQUESTS"
            elif response.status_code == 503:
                self.stress_indicators['http_503_count'] += 1
                return False, "HTTP_503_SERVICE_UNAVAILABLE"
            elif response_time > 5.0:
                self.stress_indicators['slow_response_count'] += 1
                
            if response.status_code == 200:
                # Check if it's actually a PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                    return False, "NOT_PDF_CONTENT"
                
                # Download with streaming
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk and not self.shutdown_flag.is_set():
                            f.write(chunk)
                            
                # Validate PDF
                file_size = os.path.getsize(file_path)
                if file_size < 1024:
                    os.remove(file_path)
                    return False, "FILE_TOO_SMALL"
                    
                # Check PDF header
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header != b'%PDF':
                        os.remove(file_path)
                        return False, "INVALID_PDF_HEADER"
                
                self.performance_metrics['bandwidth_usage'] += file_size
                return True, f"SUCCESS_{file_size}"
                
            else:
                return False, f"HTTP_{response.status_code}"
                
        except requests.exceptions.Timeout:
            self.stress_indicators['timeout_count'] += 1
            return False, "TIMEOUT"
        except requests.exceptions.ConnectionError:
            self.stress_indicators['connection_reset_count'] += 1
            return False, "CONNECTION_ERROR"
        except Exception as e:
            return False, f"ERROR_{str(e)}"
    
    def worker_thread(self, url_queue, results_queue, worker_id):
        """Worker thread for downloading files"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': f'UltraAggressive-Worker-{worker_id}/1.0'
        })
        
        while not self.shutdown_flag.is_set():
            try:
                url = url_queue.get(timeout=1)
                if url is None:  # Poison pill
                    break
                    
                self.performance_metrics['concurrent_connections'] += 1
                if self.performance_metrics['concurrent_connections'] > self.performance_metrics['max_concurrent']:
                    self.performance_metrics['max_concurrent'] = self.performance_metrics['concurrent_connections']
                
                success, result = self.download_single_file(url, session)
                
                self.performance_metrics['total_requests'] += 1
                if success:
                    self.performance_metrics['successful_downloads'] += 1
                else:
                    self.performance_metrics['failed_requests'] += 1
                
                results_queue.put((url, success, result))
                self.performance_metrics['concurrent_connections'] -= 1
                
                url_queue.task_done()
                
                # Adaptive delay based on current RPS setting
                time.sleep(self.current_delay)
                
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                self.performance_metrics['concurrent_connections'] -= 1
    
    def rps_escalation_monitor(self):
        """Monitor and escalate RPS based on schedule"""
        start_time = time.time()
        
        while not self.shutdown_flag.is_set():
            elapsed = time.time() - start_time
            
            for interval, target_rps in self.escalation_intervals:
                if elapsed >= interval and self.performance_metrics['current_rps'] < target_rps:
                    # Check server stress before escalating
                    if self.check_server_health():
                        old_rps = self.performance_metrics['current_rps']
                        self.performance_metrics['current_rps'] = target_rps
                        self.current_delay = 1.0 / target_rps
                        self.logger.info(f"🚀 ESCALATING RPS: {old_rps} → {target_rps} RPS (delay: {self.current_delay:.4f}s)")
                    else:
                        self.logger.warning(f"⚠️  Server stress detected. Holding RPS at {self.performance_metrics['current_rps']}")
                    break
                    
            time.sleep(30)  # Check every 30 seconds
    
    def check_server_health(self):
        """Check if server can handle increased load"""
        # Don't escalate if too many server errors
        total_errors = (self.stress_indicators['http_429_count'] + 
                       self.stress_indicators['http_503_count'] + 
                       self.stress_indicators['timeout_count'])
        
        if total_errors > 100:  # More than 100 server stress indicators
            return False
            
        # Don't escalate if average response time is too high
        if self.performance_metrics['response_times']:
            avg_response_time = sum(self.performance_metrics['response_times'][-50:]) / min(50, len(self.performance_metrics['response_times']))
            if avg_response_time > 3.0:  # Average response time > 3 seconds
                return False
        
        return True
    
    def performance_monitor(self):
        """Monitor and report performance metrics"""
        while not self.shutdown_flag.is_set():
            time.sleep(60)  # Report every minute
            
            elapsed = time.time() - self.performance_metrics['start_time'].timestamp()
            actual_rps = self.performance_metrics['total_requests'] / elapsed if elapsed > 0 else 0
            
            success_rate = (self.performance_metrics['successful_downloads'] / 
                          self.performance_metrics['total_requests'] * 100 
                          if self.performance_metrics['total_requests'] > 0 else 0)
            
            avg_response_time = (sum(self.performance_metrics['response_times'][-100:]) / 
                               min(100, len(self.performance_metrics['response_times']))
                               if self.performance_metrics['response_times'] else 0)
            
            bandwidth_mb = self.performance_metrics['bandwidth_usage'] / 1024 / 1024
            
            report = f"""
🔥 ULTRA AGGRESSIVE PERFORMANCE REPORT 🔥
Time: {elapsed:.0f}s | Target RPS: {self.performance_metrics['current_rps']} | Actual RPS: {actual_rps:.1f}
Downloads: {self.performance_metrics['successful_downloads']} | Success Rate: {success_rate:.1f}%
Max Concurrent: {self.performance_metrics['max_concurrent']} | Bandwidth: {bandwidth_mb:.1f} MB
Avg Response: {avg_response_time:.3f}s | Server Errors: 429={self.stress_indicators['http_429_count']}, 503={self.stress_indicators['http_503_count']}, TO={self.stress_indicators['timeout_count']}
            """
            
            self.logger.info(report)
    
    def load_batch_urls(self, batch_file):
        """Load URLs from batch file - handles pipe-separated format"""
        urls = []
        try:
            with open(batch_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        # Handle pipe-separated format: URL|ministry|filename
                        if '|' in line:
                            url_part = line.split('|')[0].strip()
                            urls.append(url_part)
                        else:
                            urls.append(line)
        except Exception as e:
            self.logger.error(f"Error loading batch file {batch_file}: {e}")
        return urls
    
    def process_batch_ultra_aggressive(self, batch_file):
        """Process a batch with ultra-aggressive settings"""
        self.logger.info(f"🚀 LAUNCHING ULTRA AGGRESSIVE ASSAULT ON: {batch_file}")
        
        urls = self.load_batch_urls(batch_file)
        if not urls:
            self.logger.error(f"No URLs loaded from {batch_file}")
            return
            
        self.logger.info(f"📡 TARGETING {len(urls)} REGULATIONS - MAXIMUM AGGRESSION DEPLOYED")
        
        # Create queues
        url_queue = Queue()
        results_queue = Queue()
        
        # Load URLs into queue
        for url in urls:
            url_queue.put(url)
        
        # Start monitoring threads
        rps_monitor = threading.Thread(target=self.rps_escalation_monitor, daemon=True)
        rps_monitor.start()
        
        perf_monitor = threading.Thread(target=self.performance_monitor, daemon=True)
        perf_monitor.start()
        
        # Start worker threads
        workers = []
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self.worker_thread,
                args=(url_queue, results_queue, i),
                daemon=True
            )
            worker.start()
            workers.append(worker)
        
        # Monitor progress
        processed = 0
        total_urls = len(urls)
        
        while processed < total_urls and not self.shutdown_flag.is_set():
            try:
                url, success, result = results_queue.get(timeout=5)
                processed += 1
                
                if success:
                    self.logger.info(f"✅ SUCCESS [{processed}/{total_urls}]: {result}")
                else:
                    self.logger.warning(f"❌ FAILED [{processed}/{total_urls}]: {result}")
                    
                # Progress milestone
                if processed % 100 == 0:
                    elapsed = time.time() - self.performance_metrics['start_time'].timestamp()
                    current_rps = processed / elapsed if elapsed > 0 else 0
                    success_rate = (self.performance_metrics['successful_downloads'] / processed * 100
                                  if processed > 0 else 0)
                    
                    self.logger.info(f"🎯 MILESTONE: {processed}/{total_urls} ({processed/total_urls*100:.1f}%) | "
                                   f"RPS: {current_rps:.1f} | Success: {success_rate:.1f}%")
                
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing results: {e}")
        
        # Shutdown workers
        for _ in workers:
            url_queue.put(None)  # Poison pills
            
        for worker in workers:
            worker.join(timeout=10)
        
        self.logger.info(f"🏁 BATCH COMPLETE: {batch_file} | Processed: {processed}/{total_urls}")
    
    def run_parallel_ministry_assault(self):
        """Run parallel assault on multiple ministries simultaneously"""
        self.logger.info("🔥🔥🔥 INITIATING PARALLEL MINISTRY ASSAULT 🔥🔥🔥")
        self.logger.info(f"TARGET: {self.initial_rps} RPS → {self.target_rps}+ RPS")
        self.logger.info(f"PARALLEL STREAMS: {self.concurrent_ministry_streams}")
        
        # Get available batch files
        batch_files = []
        for i in range(1, 41):  # 40 batches
            batch_file = os.path.join(self.batch_dir, f"batch_{i:04d}.txt")
            if os.path.exists(batch_file):
                batch_files.append(batch_file)
        
        self.logger.info(f"📂 LOADED {len(batch_files)} BATCH FILES FOR ASSAULT")
        
        # Start with priority batches (assume they contain high-priority ministries)
        priority_batches = batch_files[:10]  # First 10 batches likely have priority ministries
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=self.concurrent_ministry_streams) as executor:
            futures = []
            
            for batch_file in priority_batches:
                if self.shutdown_flag.is_set():
                    break
                    
                future = executor.submit(self.process_batch_ultra_aggressive, batch_file)
                futures.append((future, batch_file))
                
                # Stagger batch starts
                time.sleep(2)
            
            # Wait for completion
            for future, batch_file in futures:
                try:
                    future.result(timeout=3600)  # 1 hour timeout per batch
                except Exception as e:
                    self.logger.error(f"Batch {batch_file} failed: {e}")
        
        self.logger.info("🏆 PARALLEL MINISTRY ASSAULT COMPLETE")
        self.save_performance_report()
    
    def save_performance_report(self):
        """Save comprehensive performance report"""
        report_file = os.path.join(self.base_dir, "ultra_aggressive_performance_report.json")
        
        elapsed = time.time() - self.performance_metrics['start_time'].timestamp()
        actual_rps = self.performance_metrics['total_requests'] / elapsed if elapsed > 0 else 0
        
        report = {
            'mission_summary': {
                'start_time': self.performance_metrics['start_time'].isoformat(),
                'duration_seconds': elapsed,
                'target_rps': self.target_rps,
                'max_achieved_rps': max(actual_rps, self.performance_metrics['current_rps']),
                'actual_average_rps': actual_rps,
            },
            'performance_metrics': self.performance_metrics,
            'stress_indicators': self.stress_indicators,
            'success_metrics': {
                'total_requests': self.performance_metrics['total_requests'],
                'successful_downloads': self.performance_metrics['successful_downloads'],
                'success_rate_percent': (self.performance_metrics['successful_downloads'] / 
                                       self.performance_metrics['total_requests'] * 100
                                       if self.performance_metrics['total_requests'] > 0 else 0),
                'bandwidth_mb': self.performance_metrics['bandwidth_usage'] / 1024 / 1024,
                'max_concurrent_connections': self.performance_metrics['max_concurrent'],
            }
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"📊 Performance report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save performance report: {e}")

def main():
    """Main execution function"""
    print("🔥🔥🔥 ULTRA AGGRESSIVE MINISTERIAL DOWNLOADER 🔥🔥🔥")
    print("⚡ EXTREME RPS TESTING: 25 → 100+ RPS")
    print("🎯 PARALLEL MINISTRY PROCESSING")
    print("💥 MAXIMUM SERVER ASSAULT INITIATED")
    print("-" * 60)
    
    downloader = UltraAggressiveDownloader()
    
    try:
        downloader.run_parallel_ministry_assault()
    except KeyboardInterrupt:
        downloader.logger.info("🛑 ULTRA AGGRESSIVE ASSAULT TERMINATED BY USER")
    except Exception as e:
        downloader.logger.error(f"💥 CRITICAL ERROR: {e}")
    finally:
        downloader.save_performance_report()
        print("\n🏁 ULTRA AGGRESSIVE MISSION COMPLETE")

if __name__ == "__main__":
    main()