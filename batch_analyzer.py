#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path

def get_file_sizes():
    """Get sizes of all untracked files."""
    result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], 
                          capture_output=True, text=True, cwd='.')
    
    files = []
    total_size = 0
    
    for file_path in result.stdout.strip().split('\n'):
        if file_path:
            try:
                size = os.path.getsize(file_path)
                files.append({
                    'path': file_path,
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                })
                total_size += size
            except FileNotFoundError:
                # Skip files that might have been deleted
                continue
    
    return files, total_size

def create_batches(files, max_size_mb=95):  # Use 95MB to leave buffer
    """Create batches under the size limit."""
    batches = []
    current_batch = []
    current_size = 0
    max_size_bytes = max_size_mb * 1024 * 1024
    
    # Sort files by size (smaller first for better packing)
    files.sort(key=lambda x: x['size'])
    
    for file_info in files:
        if current_size + file_info['size'] <= max_size_bytes:
            current_batch.append(file_info)
            current_size += file_info['size']
        else:
            if current_batch:
                batches.append({
                    'files': current_batch,
                    'total_size': current_size,
                    'total_size_mb': round(current_size / (1024 * 1024), 2),
                    'file_count': len(current_batch)
                })
            current_batch = [file_info]
            current_size = file_info['size']
    
    # Add the last batch
    if current_batch:
        batches.append({
            'files': current_batch,
            'total_size': current_size,
            'total_size_mb': round(current_size / (1024 * 1024), 2),
            'file_count': len(current_batch)
        })
    
    return batches

def main():
    os.chdir('/root/.openclaw/peraturan-perundang-undangan-pdf')
    
    print("🔍 Analyzing untracked files...")
    files, total_size = get_file_sizes()
    
    print(f"📊 Found {len(files)} files, Total: {round(total_size / (1024 * 1024), 2)}MB")
    
    if not files:
        print("✅ No files to process!")
        return
    
    batches = create_batches(files)
    
    print(f"📦 Created {len(batches)} batches:")
    for i, batch in enumerate(batches, 1):
        print(f"  Batch {i}: {batch['file_count']} files, {batch['total_size_mb']}MB")
    
    # Save batch plan
    with open('batch_plan.json', 'w') as f:
        json.dump({
            'total_files': len(files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'batches': batches
        }, f, indent=2)
    
    print("💾 Batch plan saved to batch_plan.json")

if __name__ == "__main__":
    main()