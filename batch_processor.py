#!/usr/bin/env python3
import json
import subprocess
import os
import sys
import time
from datetime import datetime

def run_command(cmd, cwd='.'):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def process_batch(batch_num, batch_info):
    """Process a single batch - add files, commit, and push."""
    print(f"\n🔄 Processing Batch {batch_num}/{total_batches}")
    print(f"   Files: {batch_info['file_count']}, Size: {batch_info['total_size_mb']}MB")
    
    # Add files to git
    files_to_add = [f['path'] for f in batch_info['files']]
    
    # Add files in chunks to avoid command line length limits
    chunk_size = 100
    for i in range(0, len(files_to_add), chunk_size):
        chunk = files_to_add[i:i+chunk_size]
        files_str = ' '.join([f'"{f}"' for f in chunk])
        success, stdout, stderr = run_command(f'git add {files_str}')
        if not success:
            print(f"❌ Failed to add files: {stderr}")
            return False
    
    # Create commit message
    commit_msg = f"""Batch {batch_num}/{total_batches}: Add {batch_info['file_count']} legal documents ({batch_info['total_size_mb']}MB)

- Indonesian legal database expansion
- Organized structure: permen, perda, pp, uu, constitutional, perpres
- Systematic categorization by ministry and region
- PDF documents for legal research and compliance"""
    
    # Commit
    success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        return False
    
    print(f"✅ Committed batch {batch_num}")
    
    # Push immediately
    success, stdout, stderr = run_command('git push origin master')
    if not success:
        print(f"❌ Failed to push batch {batch_num}: {stderr}")
        return False
    
    print(f"🚀 Pushed batch {batch_num} successfully")
    
    # Small delay to be nice to GitHub
    time.sleep(2)
    return True

def main():
    global total_batches
    
    os.chdir('/root/.openclaw/peraturan-perundang-undangan-pdf')
    
    # Load batch plan
    try:
        with open('batch_plan.json', 'r') as f:
            plan = json.load(f)
    except FileNotFoundError:
        print("❌ batch_plan.json not found. Run batch_analyzer.py first.")
        sys.exit(1)
    
    batches = plan['batches']
    total_batches = len(batches)
    
    print(f"🚀 Starting batch processing for PDF repository")
    print(f"📦 {total_batches} batches to process")
    print(f"📊 Total: {plan['total_files']} files, {plan['total_size_mb']}MB")
    
    # Process each batch
    successful_batches = 0
    start_time = datetime.now()
    
    for i, batch in enumerate(batches, 1):
        if process_batch(i, batch):
            successful_batches += 1
            print(f"✅ Progress: {successful_batches}/{total_batches} batches complete")
        else:
            print(f"❌ Failed at batch {i}. Stopping.")
            break
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n🎯 PDF Repository Processing Complete!")
    print(f"✅ Successfully processed: {successful_batches}/{total_batches} batches")
    print(f"⏱️  Duration: {duration}")
    
    if successful_batches == total_batches:
        print("🎉 All PDF repository changes committed and pushed successfully!")
        
        # Clean up
        os.remove('batch_plan.json')
        os.remove('batch_analyzer.py')
        print("🧹 Cleaned up temporary files")
        
        return True
    else:
        print(f"⚠️  {total_batches - successful_batches} batches failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)