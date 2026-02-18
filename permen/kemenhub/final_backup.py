#!/usr/bin/env python3
"""
FINAL KEMENHUB EMERGENCY BACKUP
Mission: Work with existing metadata to complete the backup
Author: Emergency Data Preservation Agent - Final Attempt
"""

import json
import os
import requests
import re
import time
import logging
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WORK_DIR = "/root/.openclaw/workspace/permen/kemenhub"
PDF_DIR = os.path.join(WORK_DIR, 'pdfs')
MARKDOWN_DIR = os.path.join(WORK_DIR, 'markdown')

class FinalBackup:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*'
        })
        os.makedirs(PDF_DIR, exist_ok=True)
        os.makedirs(MARKDOWN_DIR, exist_ok=True)
        
    def extract_pdf_links(self, regulation):
        """Get PDF links for a regulation"""
        try:
            response = self.session.get(regulation['detail_url'], timeout=30)
            response.raise_for_status()
            
            # Extract API media links
            api_pattern = r'/api/media\?data=([a-zA-Z0-9+/=]+)'
            api_matches = re.findall(api_pattern, response.text)
            
            pdf_links = []
            for match in api_matches:
                pdf_links.append(f"https://jdih.dephub.go.id/api/media?data={match}")
            
            # Extract filename
            filename_pattern = r'<button[^>]*>([^<]*\.pdf)</button>'
            filename_match = re.search(filename_pattern, response.text, re.IGNORECASE)
            filename = filename_match.group(1) if filename_match else None
            
            return pdf_links, filename
            
        except Exception as e:
            logger.error(f"Error getting PDF links for {regulation['title']}: {e}")
            return [], None
    
    def download_pdf(self, pdf_url, filepath, referer):
        """Download a single PDF"""
        try:
            headers = {'Referer': referer, 'Accept': 'application/pdf,*/*'}
            response = self.session.get(pdf_url, timeout=120, headers=headers)
            response.raise_for_status()
            
            if b'%PDF' in response.content[:10]:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                logger.warning(f"Response doesn't look like PDF")
                return False
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def extract_text(self, pdf_path):
        """Extract text from PDF"""
        try:
            # Install pdftotext if needed
            subprocess.run(['apt', 'update'], check=False, capture_output=True)
            subprocess.run(['apt', 'install', '-y', 'poppler-utils'], check=False, capture_output=True)
            
            result = subprocess.run([
                'pdftotext', '-layout', '-nopgbrk', pdf_path, '-'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and result.stdout:
                return result.stdout
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
        
        return None
    
    def create_markdown(self, regulation, text):
        """Create markdown file"""
        title = regulation['title']
        
        # Generate filename
        number_match = re.search(r'PM\s+(\d+)', title, re.IGNORECASE)
        year_match = re.search(r'Tahun\s+(\d{4})', title, re.IGNORECASE)
        
        if number_match and year_match:
            number = number_match.group(1).zfill(2)
            year = year_match.group(1)
            filename = f"permen-kemenhub-{number}-{year}.md"
        else:
            safe_title = re.sub(r'[^\w\-_\.]', '_', title).lower()
            filename = f"permen-kemenhub-{safe_title}.md"
        
        # Clean text
        if text:
            lines = text.split('\n')
            cleaned_lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in lines if line.strip()]
            cleaned_text = '\n'.join(cleaned_lines)
            cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        else:
            cleaned_text = "ERROR: Could not extract text from PDF"
        
        # Create markdown content
        markdown = f"# {title}\n\n"
        markdown += "## Metadata\n\n"
        markdown += f"- **Judul:** {title}\n"
        markdown += f"- **URL:** {regulation.get('detail_url', 'N/A')}\n"
        markdown += f"- **Tanggal Backup:** 2026-02-18\n\n"
        markdown += "## Isi Peraturan\n\n"
        markdown += "```\n"
        markdown += cleaned_text
        markdown += "\n```\n\n"
        markdown += "---\n"
        markdown += "*EMERGENCY BACKUP - RAW DATA ONLY*\n"
        
        markdown_path = os.path.join(MARKDOWN_DIR, filename)
        
        try:
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            return True
        except Exception as e:
            logger.error(f"Error writing markdown: {e}")
            return False
    
    def process_regulation(self, regulation):
        """Process one regulation"""
        logger.info(f"Processing: {regulation['title']}")
        
        # Get PDF links
        pdf_links, pdf_filename = self.extract_pdf_links(regulation)
        if not pdf_links:
            logger.error(f"No PDF links found for: {regulation['title']}")
            return False
        
        # Try to download PDF
        if pdf_filename:
            filename = pdf_filename
        else:
            filename = f"{re.sub(r'[^\\w\\-_\\.]', '_', regulation['title'])}.pdf"
        
        pdf_path = os.path.join(PDF_DIR, filename)
        
        # Try each PDF link
        downloaded = False
        for i, pdf_url in enumerate(pdf_links):
            logger.info(f"Trying PDF link {i+1}/{len(pdf_links)}")
            if self.download_pdf(pdf_url, pdf_path, regulation['detail_url']):
                logger.info(f"Downloaded: {filename}")
                downloaded = True
                break
        
        if not downloaded:
            logger.error(f"Failed to download PDF for: {regulation['title']}")
            # Still try to create markdown with error message
            self.create_markdown(regulation, None)
            return False
        
        # Extract text
        text = self.extract_text(pdf_path)
        
        # Create markdown
        if self.create_markdown(regulation, text):
            logger.info(f"Created markdown for: {regulation['title']}")
            return True
        
        return False

def main():
    """Main function"""
    logger.info("=== FINAL KEMENHUB EMERGENCY BACKUP ===")
    
    # Load existing metadata
    metadata_path = os.path.join(WORK_DIR, 'kemenhub_metadata.json')
    if not os.path.exists(metadata_path):
        logger.error(f"Metadata not found: {metadata_path}")
        return
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        regulations = json.load(f)
    
    logger.info(f"Found {len(regulations)} regulations in metadata")
    
    backup = FinalBackup()
    successful = 0
    failed = 0
    
    # Process first 20 regulations (or all if fewer)
    to_process = regulations[:20] if len(regulations) > 20 else regulations
    
    for i, reg in enumerate(to_process):
        logger.info(f"=== {i+1}/{len(to_process)}: {reg['title']} ===")
        if backup.process_regulation(reg):
            successful += 1
        else:
            failed += 1
        
        time.sleep(1)  # Rate limiting
    
    # Create summary
    summary = {
        'emergency_backup_completed': True,
        'processed': len(to_process),
        'successful': successful,
        'failed': failed,
        'success_rate': f"{(successful/len(to_process)*100):.1f}%" if to_process else "0%",
        'backup_date': '2026-02-18',
        'pdf_directory': PDF_DIR,
        'markdown_directory': MARKDOWN_DIR
    }
    
    summary_path = os.path.join(WORK_DIR, 'EMERGENCY_BACKUP_SUMMARY.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info("=== BACKUP COMPLETE ===")
    logger.info(f"Processed: {len(to_process)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"PDFs: {PDF_DIR}")
    logger.info(f"Markdown: {MARKDOWN_DIR}")

if __name__ == "__main__":
    main()