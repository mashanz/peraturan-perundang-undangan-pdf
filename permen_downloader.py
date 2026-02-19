#!/usr/bin/env python3
"""
PERMEN Mass Downloader - Download Indonesian ministerial regulations
Conservative rate limiting: 1 request per 2 seconds for large-scale operation
"""
import os
import sys
import time
import json
import logging
import requests
from urllib.parse import urlparse
import hashlib
import signal
from datetime import datetime
import re

class PERMENDownloader:
    def __init__(self, base_dir="/root/.openclaw/peraturan-perundang-undangan-pdf"):
        self.base_dir = base_dir
        self.permen_dir = os.path.join(base_dir, "permen")
        self.batch_dir = os.path.join(base_dir, "permen_batches")
        self.progress_file = os.path.join(base_dir, "permen_progress.json")
        self.failed_file = os.path.join(base_dir, "permen_failed.json")
        self.log_file = os.path.join(base_dir, "permen_download.log")
        
        # Conservative rate limiting for mass operation
        self.request_delay = 2.0  # 2 seconds between requests
        self.max_retries = 5
        self.initial_retry_delay = 5  # Start with 5 seconds
        
        # Progress tracking
        self.progress = self.load_progress()
        self.failed_downloads = self.load_failed()
        
        # Statistics
        self.stats = {
            'downloaded': 0,
            'failed': 0,
            'skipped': 0,
            'total_bytes': 0,
            'batch_start_time': None,
            'session_start_time': datetime.now()
        }
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # User-Agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'id,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Create ministry directories
        self.setup_directories()
        
        self.logger.info("=== PERMEN Mass Downloader Initialized ===")
        self.logger.info(f"Base directory: {self.base_dir}")
        self.logger.info(f"Rate limit: {self.request_delay} seconds per request")
        self.logger.info(f"Max retries: {self.max_retries}")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
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
        """Create ministry directories"""
        ministries = [
            'kemenkeu', 'kemendag', 'kemenhub', 'kemdikbud', 'kemkes', 'kementan',
            'esdm', 'kemkominfo', 'kemkomdigi', 'klhk', 'lhk', 'kkp', 'kemenkumham',
            'kemenag', 'kemhan', 'kemenpppa', 'atrbpn', 'bumn', 'pupr', 'ppn',
            'p2mi', 'pdt', 'haji', 'unknown'
        ]
        
        for ministry in ministries:
            ministry_dir = os.path.join(self.permen_dir, ministry)
            os.makedirs(ministry_dir, exist_ok=True)
        
        os.makedirs(self.batch_dir, exist_ok=True)
    
    def load_progress(self):
        """Load download progress from checkpoint file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_progress(self):
        """Save download progress to checkpoint file"""
        self.progress['last_updated'] = datetime.now().isoformat()
        self.progress['stats'] = self.stats.copy()
        self.progress['stats']['session_start_time'] = self.stats['session_start_time'].isoformat()
        
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def load_failed(self):
        """Load failed downloads list"""
        if os.path.exists(self.failed_file):
            try:
                with open(self.failed_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_failed(self):
        """Save failed downloads list"""
        with open(self.failed_file, 'w') as f:
            json.dump(self.failed_downloads, f, indent=2, ensure_ascii=False)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.save_progress()
        self.save_failed()
        self.print_final_stats()
        sys.exit(0)
    
    def fix_ministry_classification(self, url, ministry):
        """Fix ministry classification issues"""
        url_lower = url.lower()
        
        # Fixed mappings for misclassified ministries
        fixes = {
            'permenkkp': 'kkp',
            'permenkumham': 'kemenkumham',
            'permenag': 'kemenag',
            'permenhan': 'kemhan',
            'permenklhk': 'klhk',
            'permen-klhk': 'klhk',
            'permenlhk': 'lhk',  # sometimes they use lhk instead of klhk
            'permensos': 'kemensos',
            'permenpupr': 'pupr',
            'permenkes': 'kemkes',
            'permenkeu': 'kemenkeu',
            'pmk': 'kemenkeu',
        }
        
        if ministry == 'unknown':
            for pattern, correct_ministry in fixes.items():
                if pattern in url_lower:
                    return correct_ministry
        
        return ministry if ministry != 'unknown' else 'unknown'
    
    def generate_filepath(self, url, ministry, filename):
        """Generate full file path for download"""
        ministry = self.fix_ministry_classification(url, ministry)
        ministry_dir = os.path.join(self.permen_dir, ministry)
        return os.path.join(ministry_dir, filename)
    
    def is_valid_pdf(self, filepath):
        """Check if downloaded file is a valid PDF"""
        try:
            if os.path.getsize(filepath) < 1024:  # Less than 1KB
                return False
            
            # Check PDF header
            with open(filepath, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False
            
            return True
        except:
            return False
    
    def download_with_retry(self, url, filepath, max_retries=None):
        """Download file with exponential backoff retry logic"""
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Attempt {attempt + 1}/{max_retries}: {url}")
                
                # Make request with timeout
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    timeout=30,
                    stream=True,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    # Check if response is actually a PDF
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type or 'octet-stream' in content_type:
                        # Write file
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        # Verify PDF integrity
                        if self.is_valid_pdf(filepath):
                            file_size = os.path.getsize(filepath)
                            self.stats['total_bytes'] += file_size
                            self.logger.debug(f"✓ Downloaded: {os.path.basename(filepath)} ({file_size} bytes)")
                            return True
                        else:
                            self.logger.warning(f"Invalid PDF downloaded: {filepath}")
                            if os.path.exists(filepath):
                                os.remove(filepath)
                    else:
                        self.logger.warning(f"Non-PDF content received: {content_type}")
                
                elif response.status_code == 404:
                    self.logger.warning(f"File not found (404): {url}")
                    return False  # Don't retry 404s
                
                else:
                    self.logger.warning(f"HTTP {response.status_code}: {url}")
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1}: {url}")
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Connection error on attempt {attempt + 1}: {url}")
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            
            # Exponential backoff (only if we'll retry)
            if attempt < max_retries - 1:
                delay = self.initial_retry_delay * (2 ** attempt)
                self.logger.debug(f"Waiting {delay}s before retry...")
                time.sleep(delay)
        
        return False
    
    def process_batch_file(self, batch_file):
        """Process a single batch file"""
        batch_name = os.path.basename(batch_file)
        self.logger.info(f"Processing batch: {batch_name}")
        
        if batch_name not in self.progress:
            self.progress[batch_name] = {
                'started': datetime.now().isoformat(),
                'completed': 0,
                'total': 0,
                'last_index': 0
            }
        
        batch_progress = self.progress[batch_name]
        self.stats['batch_start_time'] = datetime.now()
        
        try:
            with open(batch_file, 'r') as f:
                lines = f.readlines()
            
            batch_progress['total'] = len(lines)
            start_index = batch_progress.get('last_index', 0)
            
            self.logger.info(f"Batch {batch_name}: {len(lines)} URLs, resuming from index {start_index}")
            
            for i, line in enumerate(lines[start_index:], start_index):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    parts = line.split('|')
                    if len(parts) != 3:
                        self.logger.warning(f"Invalid line format: {line}")
                        continue
                    
                    url, ministry, filename = parts
                    filepath = self.generate_filepath(url, ministry, filename)
                    
                    # Skip if already downloaded
                    if os.path.exists(filepath) and self.is_valid_pdf(filepath):
                        self.logger.debug(f"Skipping existing: {filename}")
                        self.stats['skipped'] += 1
                        batch_progress['completed'] += 1
                        batch_progress['last_index'] = i + 1
                        
                        # Save progress every 10 skipped files
                        if (i + 1) % 10 == 0:
                            self.save_progress()
                        continue
                    
                    # Download with rate limiting
                    self.logger.info(f"Downloading: {filename} from {ministry}")
                    success = self.download_with_retry(url, filepath)
                    
                    if success:
                        self.stats['downloaded'] += 1
                        batch_progress['completed'] += 1
                        self.logger.info(f"✓ Success: {filename}")
                    else:
                        self.stats['failed'] += 1
                        self.failed_downloads.append({
                            'url': url,
                            'ministry': ministry,
                            'filename': filename,
                            'batch': batch_name,
                            'timestamp': datetime.now().isoformat(),
                            'reason': 'download_failed'
                        })
                        self.logger.error(f"✗ Failed: {filename}")
                    
                    batch_progress['last_index'] = i + 1
                    
                    # Save progress every 10 downloads
                    if (i + 1) % 10 == 0:
                        self.save_progress()
                        self.save_failed()
                        self.print_progress_stats(batch_name, i + 1, len(lines))
                    
                    # Conservative rate limiting
                    time.sleep(self.request_delay)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    self.logger.error(f"Error processing line {i + 1}: {e}")
                    continue
            
            # Mark batch as completed
            batch_progress['completed_time'] = datetime.now().isoformat()
            self.save_progress()
            self.save_failed()
            
            batch_elapsed = datetime.now() - self.stats['batch_start_time']
            self.logger.info(f"Batch {batch_name} completed in {batch_elapsed}")
            
        except Exception as e:
            self.logger.error(f"Error processing batch {batch_name}: {e}")
            raise
    
    def print_progress_stats(self, batch_name, current, total):
        """Print progress statistics"""
        elapsed = datetime.now() - self.stats['session_start_time']
        total_processed = self.stats['downloaded'] + self.stats['failed'] + self.stats['skipped']
        
        if total_processed > 0:
            rate = total_processed / elapsed.total_seconds() * 3600  # per hour
            mb_downloaded = self.stats['total_bytes'] / (1024 * 1024)
            
            self.logger.info(f"Progress [{batch_name}]: {current}/{total} | "
                           f"Session: D:{self.stats['downloaded']} "
                           f"F:{self.stats['failed']} S:{self.stats['skipped']} | "
                           f"Rate: {rate:.1f}/hr | {mb_downloaded:.1f}MB")
    
    def print_final_stats(self):
        """Print final statistics"""
        elapsed = datetime.now() - self.stats['session_start_time']
        total_processed = self.stats['downloaded'] + self.stats['failed'] + self.stats['skipped']
        mb_downloaded = self.stats['total_bytes'] / (1024 * 1024)
        
        self.logger.info("=== FINAL STATISTICS ===")
        self.logger.info(f"Session time: {elapsed}")
        self.logger.info(f"Total processed: {total_processed}")
        self.logger.info(f"Downloaded: {self.stats['downloaded']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Skipped: {self.stats['skipped']}")
        self.logger.info(f"Data downloaded: {mb_downloaded:.1f} MB")
        
        if elapsed.total_seconds() > 0:
            rate = total_processed / elapsed.total_seconds() * 3600
            self.logger.info(f"Average rate: {rate:.1f} files/hour")
        
        if self.stats['failed'] > 0:
            self.logger.info(f"Failed downloads logged to: {self.failed_file}")
    
    def run_mass_download(self, start_batch=1, end_batch=None):
        """Run the mass download operation"""
        # Find all batch files
        batch_files = []
        for i in range(1, 100):  # Check up to 100 batches
            batch_file = os.path.join(self.batch_dir, f"batch_{i:04d}.txt")
            if os.path.exists(batch_file):
                batch_files.append(batch_file)
            else:
                break
        
        if not batch_files:
            self.logger.error(f"No batch files found in {self.batch_dir}")
            return False
        
        # Filter batch range
        if end_batch is None:
            end_batch = len(batch_files)
        
        selected_batches = batch_files[start_batch-1:end_batch]
        
        self.logger.info(f"Starting mass download: {len(selected_batches)} batches")
        self.logger.info(f"Batch range: {start_batch} to {min(end_batch, len(batch_files))}")
        
        try:
            for i, batch_file in enumerate(selected_batches, 1):
                self.logger.info(f"=== BATCH {start_batch + i - 1}/{len(batch_files)} ===")
                self.process_batch_file(batch_file)
                
                # Save checkpoint after each batch
                self.save_progress()
                self.save_failed()
                
                # Brief pause between batches
                if i < len(selected_batches):
                    self.logger.info("Brief pause between batches...")
                    time.sleep(10)
        
        except KeyboardInterrupt:
            self.logger.info("Download interrupted by user")
        except Exception as e:
            self.logger.error(f"Fatal error during mass download: {e}")
            raise
        finally:
            self.save_progress()
            self.save_failed()
            self.print_final_stats()
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PERMEN Mass Downloader')
    parser.add_argument('--start-batch', type=int, default=1, help='Starting batch number')
    parser.add_argument('--end-batch', type=int, help='Ending batch number (inclusive)')
    parser.add_argument('--test', action='store_true', help='Test mode: download only first 5 files from batch 1')
    
    args = parser.parse_args()
    
    downloader = PERMENDownloader()
    
    if args.test:
        print("=== TEST MODE ===")
        print("Downloading first 5 files from batch 1 for testing...")
        # Create a test batch file
        batch_file = "/root/.openclaw/peraturan-perundang-undangan-pdf/permen_batches/batch_0001.txt"
        if os.path.exists(batch_file):
            with open(batch_file, 'r') as f:
                lines = f.readlines()[:5]  # Only first 5 lines
            
            test_batch = "/tmp/test_batch.txt"
            with open(test_batch, 'w') as f:
                f.writelines(lines)
            
            downloader.process_batch_file(test_batch)
            os.remove(test_batch)
        else:
            print(f"Batch file not found: {batch_file}")
        return
    
    # Run full mass download
    success = downloader.run_mass_download(args.start_batch, args.end_batch)
    
    if success:
        print("Mass download operation completed successfully!")
    else:
        print("Mass download operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()