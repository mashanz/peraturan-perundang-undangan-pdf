#!/usr/bin/env python3
"""
Regional Regulations (PERDA) Downloader
Extracts and downloads PDF files for PERDA, PERGUB, PERBUP/PERWALI regulations
"""

import requests
import time
import re
import os
import sys
from urllib.parse import urljoin, urlparse
from pathlib import Path
import json
from datetime import datetime

# Configuration
BASE_DIR = Path("/root/.openclaw/peraturan-perundang-undangan-pdf/perda")
LOG_DIR = BASE_DIR / "logs"
FAILED_DIR = BASE_DIR / "failed"
RATE_LIMIT = 1.5  # seconds between requests
MAX_RETRIES = 3
CHUNK_SIZE = 8192
MIN_PDF_SIZE = 1000  # bytes
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def setup_directories():
    """Create necessary directories"""
    LOG_DIR.mkdir(exist_ok=True)
    FAILED_DIR.mkdir(exist_ok=True)
    
    # Create regional subdirectories
    for region_type in ["provinsi", "kabupaten", "kota"]:
        (BASE_DIR / region_type).mkdir(exist_ok=True)

def log_message(message, level="INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    print(log_entry)
    
    # Also write to log file
    with open(LOG_DIR / "download.log", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def extract_pdf_url(regulation_url):
    """Extract PDF download URL from regulation page"""
    try:
        response = requests.get(regulation_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Look for PDF download links
        pdf_patterns = [
            r'href="([^"]*\.pdf)"',
            r'href="([^"]*download[^"]*)"',
            r'href="([^"]*\.pdf\?[^"]*)"',
        ]
        
        content = response.text
        
        for pattern in pdf_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    return match
                elif match.startswith('/'):
                    return urljoin(regulation_url, match)
        
        # Alternative: look for data-url attributes or onclick handlers
        data_url_pattern = r'data-url="([^"]*\.pdf[^"]*)"'
        matches = re.findall(data_url_pattern, content, re.IGNORECASE)
        if matches:
            pdf_url = matches[0]
            if pdf_url.startswith('http'):
                return pdf_url
            elif pdf_url.startswith('/'):
                return urljoin(regulation_url, pdf_url)
        
        return None
        
    except Exception as e:
        log_message(f"Error extracting PDF URL from {regulation_url}: {e}", "ERROR")
        return None

def determine_file_path(regulation_url):
    """Determine the appropriate file path based on regulation type"""
    # Extract regulation details from URL
    url_path = urlparse(regulation_url).path
    
    if "perda-provinsi-" in url_path:
        region_type = "provinsi"
        region_name = url_path.split("perda-provinsi-")[1].split("-no-")[0]
    elif "perda-kabupaten-" in url_path:
        region_type = "kabupaten"  
        region_name = url_path.split("perda-kabupaten-")[1].split("-no-")[0]
    elif "perda-kota-" in url_path:
        region_type = "kota"
        region_name = url_path.split("perda-kota-")[1].split("-no-")[0]
    else:
        region_type = "misc"
        region_name = "unknown"
    
    # Extract regulation number and year
    reg_match = re.search(r"no-(\d+)-tahun-(\d+)", url_path)
    if reg_match:
        reg_num, year = reg_match.groups()
        filename = f"perda-{region_type}-{region_name}-{reg_num}-{year}.pdf"
    else:
        # Fallback filename
        filename = url_path.split('/')[-1] + ".pdf"
    
    # Create directory structure
    target_dir = BASE_DIR / region_type / region_name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    return target_dir / filename

def validate_pdf(file_path):
    """Validate that the downloaded file is a proper PDF"""
    if not file_path.exists():
        return False, "File does not exist"
    
    if file_path.stat().st_size < MIN_PDF_SIZE:
        return False, f"File too small ({file_path.stat().st_size} bytes)"
    
    # Check PDF header
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if not header.startswith(b'%PDF'):
                return False, "Invalid PDF header"
    except Exception as e:
        return False, f"Cannot read file: {e}"
    
    return True, "Valid PDF"

def download_pdf(pdf_url, target_path, regulation_url):
    """Download PDF file with validation"""
    try:
        response = requests.get(pdf_url, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' not in content_type and 'pdf' not in content_type:
            log_message(f"Warning: Unexpected content type {content_type} for {pdf_url}", "WARN")
        
        # Download file
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        
        # Validate downloaded PDF
        is_valid, message = validate_pdf(target_path)
        if not is_valid:
            target_path.unlink(missing_ok=True)
            return False, f"PDF validation failed: {message}"
        
        log_message(f"Successfully downloaded: {target_path.name}")
        return True, "Download successful"
        
    except Exception as e:
        target_path.unlink(missing_ok=True)
        return False, f"Download error: {e}"

def process_regulation(regulation_url, retry_count=0):
    """Process a single regulation URL"""
    try:
        log_message(f"Processing: {regulation_url}")
        
        # Determine target file path
        target_path = determine_file_path(regulation_url)
        
        # Skip if already exists and valid
        if target_path.exists():
            is_valid, message = validate_pdf(target_path)
            if is_valid:
                log_message(f"Skipping existing valid PDF: {target_path.name}")
                return True, "Already exists"
        
        # Extract PDF URL
        pdf_url = extract_pdf_url(regulation_url)
        if not pdf_url:
            return False, "No PDF URL found"
        
        log_message(f"Found PDF URL: {pdf_url}")
        
        # Download PDF
        success, message = download_pdf(pdf_url, target_path, regulation_url)
        
        if success:
            return True, message
        else:
            if retry_count < MAX_RETRIES:
                log_message(f"Retrying {regulation_url} (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(RATE_LIMIT * 2)  # Longer delay for retries
                return process_regulation(regulation_url, retry_count + 1)
            else:
                # Save to failed list
                with open(FAILED_DIR / "failed_downloads.txt", "a") as f:
                    f.write(f"{regulation_url}\t{message}\n")
                return False, message
        
    except Exception as e:
        log_message(f"Unexpected error processing {regulation_url}: {e}", "ERROR")
        return False, f"Unexpected error: {e}"

def main():
    """Main download process"""
    setup_directories()
    
    # Load regulation URLs
    url_file = BASE_DIR / "clean-regional-regulations-list.txt"
    if not url_file.exists():
        log_message("URL file not found: clean-regional-regulations-list.txt", "ERROR")
        sys.exit(1)
    
    with open(url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    log_message(f"Starting download of {len(urls)} regional regulations")
    
    # Statistics
    successful = 0
    failed = 0
    skipped = 0
    
    # Process each URL
    for i, url in enumerate(urls, 1):
        log_message(f"Progress: {i}/{len(urls)} ({i/len(urls)*100:.1f}%)")
        
        try:
            success, message = process_regulation(url)
            if success:
                if "Already exists" in message:
                    skipped += 1
                else:
                    successful += 1
            else:
                failed += 1
                log_message(f"Failed: {url} - {message}", "ERROR")
            
            # Rate limiting
            time.sleep(RATE_LIMIT)
            
            # Progress report every 100 items
            if i % 100 == 0:
                log_message(f"Progress Report: {successful} successful, {failed} failed, {skipped} skipped")
            
        except KeyboardInterrupt:
            log_message("Download interrupted by user", "WARN")
            break
        except Exception as e:
            log_message(f"Unexpected error in main loop: {e}", "ERROR")
            failed += 1
    
    # Final statistics
    log_message(f"Download complete: {successful} successful, {failed} failed, {skipped} skipped")
    
    # Generate completion report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_processed": len(urls),
        "successful": successful,
        "failed": failed,
        "skipped": skipped,
        "success_rate": successful / (successful + failed) * 100 if (successful + failed) > 0 else 0
    }
    
    with open(LOG_DIR / "completion_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    log_message(f"Completion report saved to {LOG_DIR / 'completion_report.json'}")

if __name__ == "__main__":
    main()