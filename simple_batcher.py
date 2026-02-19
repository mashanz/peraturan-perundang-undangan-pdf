#!/usr/bin/env python3
import os
import subprocess
import json
import time

def run_git(cmd):
    """Run git command safely."""
    result = subprocess.run(f'git {cmd}', shell=True, capture_output=True, text=True, cwd='.')
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def get_untracked_files():
    """Get list of untracked files."""
    success, stdout, stderr = run_git('ls-files --others --exclude-standard')
    if success:
        return [f for f in stdout.split('\n') if f.strip()]
    return []

def get_file_size(filepath):
    """Get file size safely."""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def process_files_in_small_batches():
    """Process files in very small batches to avoid issues."""
    os.chdir('/root/.openclaw/peraturan-perundang-undangan-pdf')
    
    files = get_untracked_files()
    if not files:
        print("✅ No files to process!")
        return True
    
    print(f"📋 Found {len(files)} files to add")
    
    batch_size = 50  # Small batches
    batch_num = 1
    total_batches = (len(files) + batch_size - 1) // batch_size
    
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i+batch_size]
        batch_size_mb = sum(get_file_size(f) for f in batch_files) / (1024*1024)
        
        print(f"\n🔄 Batch {batch_num}/{total_batches}: {len(batch_files)} files ({batch_size_mb:.1f}MB)")
        
        # Add files
        for file in batch_files:
            success, _, stderr = run_git(f'add "{file}"')
            if not success:
                print(f"⚠️  Warning: couldn't add {file}: {stderr}")
        
        # Commit
        commit_msg = f'Batch {batch_num}/{total_batches}: Add {len(batch_files)} Indonesian legal documents'
        success, stdout, stderr = run_git(f'commit -m "{commit_msg}"')
        
        if success:
            print(f"✅ Committed batch {batch_num}")
            
            # Push
            success, stdout, stderr = run_git('push origin master')
            if success:
                print(f"🚀 Pushed batch {batch_num}")
            else:
                print(f"❌ Push failed: {stderr}")
                return False
        else:
            print(f"❌ Commit failed: {stderr}")
            return False
        
        batch_num += 1
        time.sleep(1)  # Brief pause
    
    print(f"\n🎉 All {total_batches} batches processed successfully!")
    return True

if __name__ == "__main__":
    success = process_files_in_small_batches()
    if success:
        print("🧹 Cleaning up...")
        try:
            os.remove('batch_plan.json')
            os.remove('batch_analyzer.py')
            os.remove('batch_processor.py')
        except:
            pass