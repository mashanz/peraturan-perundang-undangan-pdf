#!/usr/bin/env python3
"""
Smart PDF Batch Pusher for GitHub
Automatically commits and pushes PDFs in batches under 100MB
"""

import os
import subprocess
import sys
import argparse
from pathlib import Path
import time
import json
from datetime import datetime

class PDFBatchPusher:
    def __init__(self, repo_path="/root/.openclaw/peraturan-perundang-undangan-pdf", aggressive_mode=False):
        self.repo_path = Path(repo_path)
        self.aggressive_mode = aggressive_mode
        
        # ULTRA-AGGRESSIVE MODE PARAMETERS
        if aggressive_mode:
            self.max_batch_size = 90 * 1024 * 1024  # 90MB - maximum safe size for aggressive mode
            self.max_single_file = 85 * 1024 * 1024  # 85MB max for single file in aggressive mode
            self.processing_threshold = 5 * 1024 * 1024  # 5MB minimum threshold
            self.push_delay = 15  # 15 seconds between pushes (was 30)
            self.monitoring_interval = 60  # 60 seconds monitoring (was 300)
            print("🚀 ULTRA-AGGRESSIVE MODE ACTIVATED!")
            print("├── Batch size: 90MB (maximum)")
            print("├── Processing threshold: 5MB")
            print("├── Push delay: 15 seconds")
            print("└── Monitoring interval: 60 seconds")
        else:
            self.max_batch_size = 95 * 1024 * 1024  # 95MB to stay safely under 100MB
            self.max_single_file = 90 * 1024 * 1024  # 90MB max for single file
            self.processing_threshold = 10 * 1024 * 1024  # 10MB minimum threshold
            self.push_delay = 30  # 30 seconds between pushes
            self.monitoring_interval = 300  # 5 minutes monitoring
            
        self.batch_count = 0
        self.total_pushed = 0
        self.failed_files = []
        self.session_start = datetime.now()
        self.volume_stats = {
            'total_mb_pushed': 0,
            'files_per_cycle': [],
            'avg_files_per_hour': 0,
            'push_success_rate': 100.0
        }
        
    def get_file_size(self, filepath):
        """Get file size in bytes"""
        try:
            return filepath.stat().st_size
        except:
            return 0
    
    def get_untracked_files(self):
        """Get list of untracked PDF files with sizes"""
        os.chdir(self.repo_path)
        
        # Get git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        files_with_sizes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
                
            status = line[:2]
            filename = line[3:]
            
            # Only process untracked files and PDFs
            if status.strip() in ['??', 'A', 'M'] and filename.endswith('.pdf'):
                filepath = self.repo_path / filename
                if filepath.exists():
                    size = self.get_file_size(filepath)
                    files_with_sizes.append((filename, size, filepath))
        
        return sorted(files_with_sizes, key=lambda x: x[1])  # Sort by size
    
    def check_system_resources(self):
        """Check disk space and system resources for high-volume operations"""
        try:
            # Get disk space
            statvfs = os.statvfs(self.repo_path)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            total_space = statvfs.f_frsize * statvfs.f_blocks
            free_gb = free_space / (1024**3)
            total_gb = total_space / (1024**3)
            usage_percent = ((total_space - free_space) / total_space) * 100
            
            # Check git repository size
            try:
                result = subprocess.run(['du', '-sh', '.git'], capture_output=True, text=True, cwd=self.repo_path)
                repo_size = result.stdout.split()[0] if result.returncode == 0 else "Unknown"
            except:
                repo_size = "Unknown"
            
            return {
                'free_gb': free_gb,
                'total_gb': total_gb,
                'usage_percent': usage_percent,
                'repo_size': repo_size
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_volume_stats(self, batch_size_mb, files_count, success):
        """Update volume statistics for high-volume monitoring"""
        self.volume_stats['total_mb_pushed'] += batch_size_mb if success else 0
        self.volume_stats['files_per_cycle'].append(files_count)
        
        # Calculate success rate
        total_attempts = self.batch_count
        if total_attempts > 0:
            successful_batches = total_attempts - len(self.failed_files) // 10  # Rough estimate
            self.volume_stats['push_success_rate'] = (successful_batches / total_attempts) * 100
        
        # Calculate files per hour
        elapsed_hours = (datetime.now() - self.session_start).total_seconds() / 3600
        if elapsed_hours > 0:
            self.volume_stats['avg_files_per_hour'] = self.total_pushed / elapsed_hours
    
    def create_batches(self, files_with_sizes):
        """Group files into batches under the size limit"""
        batches = []
        current_batch = []
        current_size = 0
        large_files = []
        
        for filename, size, filepath in files_with_sizes:
            # Skip files that are too large
            if size > self.max_single_file:
                large_files.append((filename, size))
                print(f"⚠️  Skipping large file: {filename} ({size/1024/1024:.1f}MB)")
                continue
                
            # If adding this file would exceed the batch limit, start a new batch
            if current_size + size > self.max_batch_size and current_batch:
                batches.append((current_batch, current_size))
                current_batch = []
                current_size = 0
            
            current_batch.append((filename, size))
            current_size += size
        
        # Add the last batch if it's not empty
        if current_batch:
            batches.append((current_batch, current_size))
        
        return batches, large_files
    
    def commit_and_push_batch(self, batch_files, batch_size):
        """Commit and push a batch of files"""
        self.batch_count += 1
        
        try:
            # Add files to git
            files_to_add = [f[0] for f in batch_files]
            subprocess.run(['git', 'add'] + files_to_add, check=True)
            
            # Create commit message
            file_count = len(batch_files)
            size_mb = batch_size / 1024 / 1024
            
            commit_msg = f"""📄 PDF Batch {self.batch_count}: {file_count} Indonesian Regulations ({size_mb:.1f}MB)

🔄 AUTOMATED BATCH COMMIT:
├── Files: {file_count} Indonesian legal regulation PDFs
├── Size: {size_mb:.1f}MB (under 100MB GitHub limit)
├── Source: peraturan.go.id mass scraping operation
└── Content: Official government legal documents

📋 FILES IN THIS BATCH:"""
            
            # Add file list to commit message (truncated if too long)
            for filename, file_size in batch_files[:10]:
                commit_msg += f"\n├── {filename} ({file_size/1024:.0f}KB)"
            
            if len(batch_files) > 10:
                commit_msg += f"\n└── ... and {len(batch_files) - 10} more files"
            
            commit_msg += f"\n\n🤖 Automated commit by batch pusher system\n📊 Total batches processed: {self.batch_count}"
            
            # Commit
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # Push
            print(f"🚀 Pushing batch {self.batch_count} ({file_count} files, {size_mb:.1f}MB)...")
            result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Batch {self.batch_count} pushed successfully!")
                self.total_pushed += file_count
                self.update_volume_stats(size_mb, file_count, True)
                return True
            else:
                print(f"❌ Push failed: {result.stderr}")
                self.update_volume_stats(size_mb, file_count, False)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Push timeout for batch {self.batch_count}")
            return False
        except Exception as e:
            print(f"❌ Error processing batch {self.batch_count}: {e}")
            return False
    
    def handle_large_files(self, large_files):
        """Handle files that are too large for normal commits"""
        if not large_files:
            return
            
        print(f"\n⚠️  LARGE FILES DETECTED ({len(large_files)} files):")
        for filename, size in large_files:
            size_mb = size / 1024 / 1024
            print(f"├── {filename}: {size_mb:.1f}MB")
        
        print("\n💡 LARGE FILE OPTIONS:")
        print("1. These files exceed 90MB limit")
        print("2. Consider using Git LFS for files >100MB")
        print("3. Or split into separate repository")
        print("4. Files are preserved locally but not committed")
        
        # Log large files for later handling
        large_files_log = {
            'timestamp': datetime.now().isoformat(),
            'large_files': [{'filename': f, 'size_mb': s/1024/1024} for f, s in large_files]
        }
        
        with open(self.repo_path / 'large_files.json', 'w') as f:
            json.dump(large_files_log, f, indent=2)
    
    def process_all_batches(self):
        """Process all untracked files in batches"""
        print("🔍 Scanning for untracked PDF files...")
        files_with_sizes = self.get_untracked_files()
        
        if not files_with_sizes:
            print("✅ No untracked PDF files found")
            return True
        
        print(f"📄 Found {len(files_with_sizes)} untracked PDF files")
        total_size = sum(size for _, size, _ in files_with_sizes)
        print(f"📊 Total size: {total_size/1024/1024:.1f}MB")
        
        # Create batches
        batches, large_files = self.create_batches(files_with_sizes)
        
        print(f"📦 Created {len(batches)} batches for processing")
        
        # Handle large files
        self.handle_large_files(large_files)
        
        # Process each batch
        success_count = 0
        for i, (batch_files, batch_size) in enumerate(batches, 1):
            print(f"\n📦 Processing batch {i}/{len(batches)}...")
            
            if self.commit_and_push_batch(batch_files, batch_size):
                success_count += 1
            else:
                # Add failed files to retry list
                self.failed_files.extend([f[0] for f in batch_files])
            
            # Wait between pushes to avoid rate limiting
            if i < len(batches):
                print(f"⏳ Waiting {self.push_delay} seconds before next batch...")
                time.sleep(self.push_delay)
        
        # Summary
        print(f"\n📊 BATCH PROCESSING COMPLETE:")
        print(f"├── Batches processed: {success_count}/{len(batches)}")
        print(f"├── Files pushed: {self.total_pushed}")
        print(f"├── Failed files: {len(self.failed_files)}")
        print(f"└── Large files skipped: {len(large_files)}")
        
        return success_count == len(batches)
    
    def monitor_and_push(self, fast_monitoring=False):
        """Monitor for new files and push them automatically"""
        interval = self.monitoring_interval
        if fast_monitoring:
            interval = 60  # Override to 60 seconds for fast monitoring
            print("⚡ FAST MONITORING MODE - 60 second intervals")
            
        print(f"🔄 Starting {'ULTRA-AGGRESSIVE' if self.aggressive_mode else 'standard'} monitoring mode (checking every {interval}s)...")
        print(f"📊 Processing threshold: {self.processing_threshold/1024/1024:.1f}MB")
        
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                current_time = datetime.now()
                elapsed = (current_time - self.session_start).total_seconds()
                
                files_with_sizes = self.get_untracked_files()
                
                if files_with_sizes:
                    total_size = sum(size for _, size, _ in files_with_sizes)
                    size_mb = total_size / 1024 / 1024
                    
                    print(f"\n⚡ CYCLE {cycle_count} - Found {len(files_with_sizes)} new PDF files ({size_mb:.1f}MB)")
                    
                    # Use aggressive threshold
                    if total_size > self.processing_threshold:
                        print(f"🚀 PROCESSING: Threshold met ({size_mb:.1f}MB > {self.processing_threshold/1024/1024:.1f}MB)")
                        self.process_all_batches()
                    else:
                        print(f"⏳ WAITING: Below threshold ({size_mb:.1f}MB < {self.processing_threshold/1024/1024:.1f}MB)")
                else:
                    # Show comprehensive volume stats even when no new files
                    resources = self.check_system_resources()
                    print(f"📊 CYCLE {cycle_count} - No new files (runtime: {elapsed/60:.1f}m)")
                    if self.aggressive_mode:
                        print(f"├── Volume pushed: {self.volume_stats['total_mb_pushed']:.1f}MB")
                        print(f"├── Files/hour rate: {self.volume_stats['avg_files_per_hour']:.1f}")
                        print(f"├── Success rate: {self.volume_stats['push_success_rate']:.1f}%")
                        if 'free_gb' in resources:
                            print(f"└── Disk space: {resources['free_gb']:.1f}GB free ({resources['usage_percent']:.1f}% used)")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print(f"\n🛑 ULTRA-AGGRESSIVE MONITORING STOPPED")
                print(f"📊 SESSION STATS:")
                print(f"├── Runtime: {elapsed/60:.1f} minutes")
                print(f"├── Cycles: {cycle_count}")
                print(f"├── Total pushed: {self.total_pushed}")
                print(f"└── Batches: {self.batch_count}")
                break
            except Exception as e:
                print(f"❌ Error in monitoring: {e}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    parser = argparse.ArgumentParser(description='Ultra-High-Speed PDF Batch Pusher for GitHub')
    parser.add_argument('--aggressive-mode', action='store_true', 
                       help='Enable ultra-aggressive batch processing (90MB batches, 5MB threshold, 15s delays)')
    parser.add_argument('--fast-monitoring', action='store_true',
                       help='Enable fast monitoring mode (60 second intervals)')
    parser.add_argument('--monitor', action='store_true',
                       help='Run in continuous monitoring mode')
    
    # Handle legacy monitor argument
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        args = parser.parse_args(['--monitor'] + sys.argv[2:])
    else:
        args = parser.parse_args()
    
    # Initialize with aggressive mode if requested
    pusher = PDFBatchPusher(aggressive_mode=args.aggressive_mode)
    
    if args.monitor or (len(sys.argv) > 1 and sys.argv[1] == "monitor"):
        # Monitoring mode
        pusher.monitor_and_push(fast_monitoring=args.fast_monitoring)
    else:
        # One-time batch processing
        success = pusher.process_all_batches()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()