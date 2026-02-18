#!/usr/bin/env python3
"""
EMERGENCY KEMENHUB DATA BACKUP SCRIPT
Mission: Extract ALL Permen Kemenhub regulations from JDIH website
Author: Emergency Data Preservation Agent
"""

import requests
import re
import json
import os
import time
from urllib.parse import urljoin, urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://jdih.dephub.go.id"
BACKUP_DIR = "/root/.openclaw/workspace/kemenhub-backup"

class KemenhubScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.regulations = []
        self.pm_regulations = []
        
    def extract_regulations_from_html(self, html_content):
        """Extract regulation links and metadata from HTML"""
        regulations = []
        
        # Pattern to find regulation entries
        pattern = r'<h3><a href="/peraturan/detail\?data=([^"]+)">([^<]+)</a></h3>'
        matches = re.findall(pattern, html_content)
        
        for match in matches:
            data_param = match[0]
            title = match[1].strip()
            
            # Check if this is a PM (Peraturan Menteri) regulation
            if title.startswith('PM '):
                regulations.append({
                    'data_param': data_param,
                    'title': title,
                    'detail_url': f"{BASE_URL}/peraturan/detail?data={data_param}",
                    'type': 'PM'
                })
                logger.info(f"Found PM regulation: {title}")
        
        return regulations
    
    def scrape_all_pages(self):
        """Scrape all pages to collect PM regulations"""
        logger.info("Starting to scrape all regulation pages...")
        page = 1
        total_pm_found = 0
        
        while True:
            logger.info(f"Scraping page {page}...")
            url = f"{BASE_URL}/peraturan?page={page}"
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Extract regulations from this page
                page_regulations = self.extract_regulations_from_html(response.text)
                
                if not page_regulations:
                    logger.info(f"No more regulations found on page {page}. Stopping.")
                    break
                
                self.pm_regulations.extend(page_regulations)
                pm_count_this_page = len(page_regulations)
                total_pm_found += pm_count_this_page
                
                logger.info(f"Page {page}: Found {pm_count_this_page} PM regulations (Total: {total_pm_found})")
                
                # Rate limiting
                time.sleep(1)
                page += 1
                
                # Safety limit to prevent infinite loops
                if page > 500:
                    logger.warning("Reached page limit of 500, stopping")
                    break
                    
            except requests.RequestException as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        logger.info(f"Scraping complete! Found {total_pm_found} total PM regulations")
        return self.pm_regulations
    
    def get_regulation_details(self, regulation):
        """Get detailed information about a regulation including PDF URL"""
        logger.info(f"Getting details for: {regulation['title']}")
        
        try:
            response = self.session.get(regulation['detail_url'], timeout=30)
            response.raise_for_status()
            
            # Look for PDF download link
            pdf_pattern = r'href="([^"]*\.pdf[^"]*)"'
            pdf_matches = re.findall(pdf_pattern, response.text, re.IGNORECASE)
            
            if pdf_matches:
                pdf_url = pdf_matches[0]
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin(BASE_URL, pdf_url)
                regulation['pdf_url'] = pdf_url
                logger.info(f"Found PDF: {pdf_url}")
            else:
                logger.warning(f"No PDF found for: {regulation['title']}")
                
            # Extract additional metadata from detail page
            regulation['html_content'] = response.text
            
            return regulation
            
        except requests.RequestException as e:
            logger.error(f"Error getting details for {regulation['title']}: {e}")
            return regulation
    
    def download_pdf(self, regulation, max_retries=3):
        """Download PDF for a regulation"""
        if 'pdf_url' not in regulation:
            logger.warning(f"No PDF URL for: {regulation['title']}")
            return False
            
        # Generate safe filename
        safe_title = re.sub(r'[^\w\-_\. ]', '_', regulation['title'])
        filename = f"{safe_title}.pdf"
        filepath = os.path.join(BACKUP_DIR, 'pdfs', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading PDF (attempt {attempt+1}): {regulation['title']}")
                response = self.session.get(regulation['pdf_url'], timeout=60)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                regulation['local_pdf_path'] = filepath
                logger.info(f"Downloaded: {filepath}")
                return True
                
            except requests.RequestException as e:
                logger.error(f"Download attempt {attempt+1} failed for {regulation['title']}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All download attempts failed for: {regulation['title']}")
                else:
                    time.sleep(5)  # Wait before retry
        
        return False
    
    def save_metadata(self):
        """Save collected metadata to JSON"""
        metadata_path = os.path.join(BACKUP_DIR, 'kemenhub_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.pm_regulations, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadata saved to: {metadata_path}")

def main():
    """Main execution function"""
    logger.info("=== EMERGENCY KEMENHUB DATA BACKUP STARTED ===")
    
    # Create backup directories
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(os.path.join(BACKUP_DIR, 'pdfs'), exist_ok=True)
    
    scraper = KemenhubScraper()
    
    # Step 1: Scrape all pages to find PM regulations
    logger.info("PHASE 1: Scraping all pages for PM regulations...")
    pm_regulations = scraper.scrape_all_pages()
    
    if not pm_regulations:
        logger.error("No PM regulations found! Exiting.")
        return
    
    # Step 2: Get detailed information for each regulation
    logger.info(f"PHASE 2: Getting detailed information for {len(pm_regulations)} PM regulations...")
    for i, reg in enumerate(pm_regulations):
        logger.info(f"Processing {i+1}/{len(pm_regulations)}: {reg['title']}")
        scraper.get_regulation_details(reg)
        time.sleep(1)  # Rate limiting
    
    # Step 3: Save metadata
    scraper.save_metadata()
    
    # Step 4: Download PDFs
    logger.info("PHASE 3: Downloading PDFs...")
    successful_downloads = 0
    for i, reg in enumerate(pm_regulations):
        logger.info(f"Downloading PDF {i+1}/{len(pm_regulations)}: {reg['title']}")
        if scraper.download_pdf(reg):
            successful_downloads += 1
        time.sleep(2)  # Rate limiting for downloads
    
    logger.info(f"=== BACKUP COMPLETE ===")
    logger.info(f"Total PM regulations found: {len(pm_regulations)}")
    logger.info(f"PDFs successfully downloaded: {successful_downloads}")
    logger.info(f"Backup location: {BACKUP_DIR}")

if __name__ == "__main__":
    main()