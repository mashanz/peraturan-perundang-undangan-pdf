#!/usr/bin/env python3
"""
EMERGENCY KEMENTAN PDF TO MARKDOWN CONVERTER
NO ANALYSIS - PURE DATA CONVERSION ONLY!
"""

import os
import sys
import logging
from pathlib import Path
import subprocess
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KementanConverter:
    def __init__(self, pdf_dir, markdown_dir, log_dir):
        self.pdf_dir = Path(pdf_dir)
        self.markdown_dir = Path(markdown_dir) 
        self.log_dir = Path(log_dir)
        
        # Create directories if they don't exist
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract raw text from PDF using pdfplumber or similar"""
        try:
            # Using pdfplumber for text extraction
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                text_content = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                
                return "\n\n".join(text_content)
                
        except ImportError:
            logger.warning("pdfplumber not available, trying pdftotext")
            try:
                result = subprocess.run([
                    'pdftotext', '-layout', str(pdf_path), '-'
                ], capture_output=True, text=True, check=True)
                return result.stdout
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to extract text from {pdf_path}: {e}")
                return None
    
    def clean_regulation_text(self, raw_text):
        """Clean and format regulation text - NO ANALYSIS"""
        if not raw_text:
            return ""
        
        lines = raw_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        
        # Join lines with proper spacing
        return '\n\n'.join(cleaned_lines)
    
    def generate_markdown_filename(self, pdf_filename):
        """Generate standardized markdown filename"""
        # Expected format: permen-kementan-XX-YYYY.md
        base_name = pdf_filename.stem.lower()
        
        # Try to extract number and year from filename
        import re
        
        # Pattern to match various naming conventions
        patterns = [
            r'permen[^0-9]*(\d+)[^0-9]+(\d{4})',  # permen-xx-yyyy
            r'peraturan[^0-9]*(\d+)[^0-9]+(\d{4})',  # peraturan-xx-yyyy  
            r'(\d+)[^0-9]+(\d{4})',  # xx-yyyy
        ]
        
        for pattern in patterns:
            match = re.search(pattern, base_name)
            if match:
                number, year = match.groups()
                return f"permen-kementan-{number:0>2s}-{year}.md"
        
        # Fallback: use original filename
        return f"{base_name}.md"
    
    def create_markdown_header(self, filename, pdf_path):
        """Create standardized markdown header"""
        return f"""# PERATURAN MENTERI PERTANIAN

**SOURCE:** {pdf_path.name}  
**CONVERTED:** {datetime.now().isoformat()}  
**FORMAT:** Raw regulation text only - NO ANALYSIS  
**STATUS:** Emergency backup conversion  

---

"""
    
    def convert_pdf_to_markdown(self, pdf_path):
        """Convert single PDF to markdown"""
        logger.info(f"Converting: {pdf_path}")
        
        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)
        if not raw_text:
            logger.error(f"Failed to extract text from {pdf_path}")
            return False
        
        # Clean text (minimal processing - preserve original structure)
        cleaned_text = self.clean_regulation_text(raw_text)
        
        # Generate filename and path
        md_filename = self.generate_markdown_filename(pdf_path)
        md_path = self.markdown_dir / md_filename
        
        # Create markdown content
        header = self.create_markdown_header(md_filename, pdf_path)
        markdown_content = header + cleaned_text
        
        # Write to file
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Successfully converted: {md_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write markdown file {md_path}: {e}")
            return False
    
    def batch_convert(self):
        """Convert all PDFs in the pdf_dir"""
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.pdf_dir}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to convert")
        
        success_count = 0
        for pdf_file in pdf_files:
            if self.convert_pdf_to_markdown(pdf_file):
                success_count += 1
        
        logger.info(f"Conversion complete: {success_count}/{len(pdf_files)} files converted")

def main():
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_markdown.py <mode>")
        print("Mode: 'batch' for all PDFs, or specific PDF filename")
        sys.exit(1)
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    pdf_dir = base_dir / "pdf-sources"
    markdown_dir = base_dir / "markdown-output"
    log_dir = base_dir / "logs"
    
    converter = KementanConverter(pdf_dir, markdown_dir, log_dir)
    
    mode = sys.argv[1]
    
    if mode == "batch":
        converter.batch_convert()
    else:
        pdf_path = pdf_dir / mode
        if pdf_path.exists():
            converter.convert_pdf_to_markdown(pdf_path)
        else:
            logger.error(f"PDF file not found: {pdf_path}")

if __name__ == "__main__":
    main()