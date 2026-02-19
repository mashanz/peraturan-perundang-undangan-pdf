#!/usr/bin/env python3
"""
Cleanup Script for Corrupted PDF Files
Identifies and handles files that are HTML pages instead of PDFs
Part of the Quality Assurance process
"""

import os
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/root/.openclaw/peraturan-perundang-undangan-pdf")

def identify_html_files():
    """Find PDF files that are actually HTML documents"""
    html_files = []
    
    for pdf_file in BASE_DIR.rglob("*.pdf"):
        if pdf_file.stat().st_size < 1000:  # Skip empty/tiny files
            continue
            
        try:
            with open(pdf_file, 'rb') as f:
                header = f.read(50)
                if b'<!DOCTYPE' in header or b'<html' in header.lower():
                    html_files.append({
                        "path": str(pdf_file),
                        "size": pdf_file.stat().st_size,
                        "name": pdf_file.name
                    })
        except Exception as e:
            print(f"Error checking {pdf_file}: {e}")
    
    return html_files

def create_redownload_list(html_files):
    """Create a list of URLs that need to be re-downloaded"""
    redownload_urls = []
    
    for file_info in html_files:
        filename = file_info["name"]
        
        # Try to reverse-engineer the URL from the filename
        # This is a best-effort approach
        if filename.startswith("perda-"):
            # Extract region info from filename
            parts = filename.replace(".pdf", "").split("-")
            if len(parts) >= 6:  # perda-type-region-num-year format
                region_type = parts[1]  # kota, kabupaten, provinsi
                region_name = "-".join(parts[2:-2])
                reg_num = parts[-2]
                year = parts[-1]
                
                url = f"https://peraturan.go.id/id/perda-{region_type}-{region_name}-no-{reg_num}-tahun-{year}"
                redownload_urls.append(url)
        
        # For other patterns, we'd need more logic
        # For now, just note them for manual review
    
    return redownload_urls

def main():
    """Main cleanup process"""
    print("Scanning for corrupted PDF files (HTML documents)...")
    
    html_files = identify_html_files()
    
    print(f"Found {len(html_files)} PDF files that are actually HTML documents:")
    
    for file_info in html_files:
        print(f"  - {file_info['name']} ({file_info['size']} bytes)")
    
    # Move corrupted files to a separate directory
    corrupted_dir = BASE_DIR / "corrupted"
    corrupted_dir.mkdir(exist_ok=True)
    
    moved_count = 0
    for file_info in html_files:
        source_path = Path(file_info["path"])
        dest_path = corrupted_dir / source_path.name
        
        try:
            source_path.rename(dest_path)
            moved_count += 1
            print(f"Moved {source_path.name} to corrupted directory")
        except Exception as e:
            print(f"Error moving {source_path.name}: {e}")
    
    print(f"Moved {moved_count} corrupted files to {corrupted_dir}")
    
    # Create redownload list
    redownload_urls = create_redownload_list(html_files)
    
    if redownload_urls:
        redownload_file = BASE_DIR / "redownload_list.txt"
        with open(redownload_file, 'w') as f:
            for url in redownload_urls:
                f.write(url + '\n')
        
        print(f"Created redownload list with {len(redownload_urls)} URLs: {redownload_file}")
    
    # Generate cleanup report
    report = {
        "timestamp": datetime.now().isoformat(),
        "corrupted_files_found": len(html_files),
        "files_moved": moved_count,
        "redownload_urls_created": len(redownload_urls),
        "corrupted_files": html_files
    }
    
    with open(BASE_DIR / "cleanup_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Cleanup complete! Report saved to cleanup_report.json")

if __name__ == "__main__":
    main()