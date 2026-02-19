#!/usr/bin/env python3
import subprocess
import os
import sys
import time
from pathlib import Path

def run_cmd(cmd, timeout=30):
    """Run command with timeout and error handling."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, 
            timeout=timeout, cwd='/root/.openclaw/peraturan-perundang-undangan-pdf'
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, '', 'Command timed out'
    except Exception as e:
        return False, '', str(e)

def get_file_size(filepath):
    """Get file size safely."""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def main():
    print("🚀 Final Batch Processor for Indonesian Legal Database")
    
    os.chdir('/root/.openclaw/peraturan-perundang-undangan-pdf')
    
    # Get all untracked files
    success, stdout, stderr = run_cmd('git ls-files --others --exclude-standard')
    if not success:
        print(f"❌ Error getting untracked files: {stderr}")
        return False
    
    files = [f for f in stdout.split('\n') if f.strip()]
    total_files = len(files)
    
    if total_files == 0:
        print("✅ No files to process!")
        return True
    
    print(f"📊 Found {total_files} files to process")
    
    # Process files in small, manageable batches
    batch_size = 10
    batch_count = 0
    processed_files = 0
    
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i+batch_size]
        actual_batch_size = len(batch_files)
        batch_count += 1
        
        print(f"\n🔄 Processing Batch {batch_count}: {actual_batch_size} files")
        
        # Add files one by one
        added_files = 0
        for file_path in batch_files:
            if os.path.exists(file_path):
                success, _, stderr = run_cmd(f'git add "{file_path}"', timeout=10)
                if success:
                    added_files += 1
                else:
                    print(f"⚠️ Warning: Could not add {file_path}: {stderr}")
            else:
                print(f"⚠️ Warning: File not found: {file_path}")
        
        if added_files == 0:
            print(f"⚠️ No files added in batch {batch_count}")
            continue
        
        # Check staging area
        success, staged_files, _ = run_cmd('git diff --cached --name-only')
        if not success or not staged_files:
            print(f"⚠️ No files staged in batch {batch_count}")
            continue
        
        staged_count = len(staged_files.split('\n')) if staged_files else 0
        print(f"📋 Staged {staged_count} files")
        
        # Create commit
        commit_msg = f"""Batch {batch_count}: Add {staged_count} Indonesian legal documents

- Indonesian legal database expansion
- Systematic organization by document type and region  
- PDF documents for legal research and compliance
- Progress: {processed_files + staged_count}/{total_files} files"""
        
        success, _, stderr = run_cmd(f'git commit -m "{commit_msg}"', timeout=15)
        if not success:
            print(f"❌ Commit failed for batch {batch_count}: {stderr}")
            continue
        
        print(f"✅ Committed batch {batch_count} with {staged_count} files")
        processed_files += staged_count
        
        # Push with retry logic
        push_attempts = 3
        push_success = False
        
        for attempt in range(push_attempts):
            print(f"🚀 Pushing batch {batch_count} (attempt {attempt + 1}/{push_attempts})...")
            success, _, stderr = run_cmd('git push origin master', timeout=60)
            
            if success:
                print(f"✅ Successfully pushed batch {batch_count}")
                push_success = True
                break
            else:
                print(f"⚠️ Push attempt {attempt + 1} failed: {stderr}")
                if attempt < push_attempts - 1:
                    print("⏳ Waiting 5 seconds before retry...")
                    time.sleep(5)
        
        if not push_success:
            print(f"❌ Failed to push batch {batch_count} after {push_attempts} attempts")
            print("🛑 Stopping to avoid issues")
            return False
        
        # Progress update
        progress_pct = (processed_files / total_files) * 100
        print(f"📈 Progress: {processed_files}/{total_files} files ({progress_pct:.1f}%)")
        
        # Brief pause between batches
        time.sleep(2)
    
    print(f"\n🎉 PDF Repository Processing Complete!")
    print(f"✅ Successfully processed {batch_count} batches")
    print(f"📊 Total files committed: {processed_files}/{total_files}")
    
    if processed_files == total_files:
        print("🎯 All files successfully committed and pushed!")
        
        # Cleanup
        print("🧹 Cleaning up temporary files...")
        cleanup_files = [
            'batch_plan.json', 'batch_analyzer.py', 'batch_processor.py', 
            'simple_batcher.py', 'quick_batcher.sh', 'final_batcher.py'
        ]
        for cleanup_file in cleanup_files:
            try:
                if os.path.exists(cleanup_file):
                    os.remove(cleanup_file)
            except:
                pass
        
        return True
    else:
        print(f"⚠️ {total_files - processed_files} files were not processed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)