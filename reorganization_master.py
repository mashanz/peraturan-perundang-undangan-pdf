#!/usr/bin/env python3
"""
INDONESIAN LEGAL DATABASE REORGANIZATION MASTER
================================================
Reorganizes PDF repository with:
1. 8-tier hierarchical structure
2. Intelligent categorization
3. Filename standardization
4. Comprehensive logging
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

class LegalDatabaseReorganizer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.filename_mappings = []
        self.categorization_log = []
        self.error_log = []
        self.stats = {
            'total_files': 0,
            'renamed_files': 0,
            'moved_files': 0,
            'categories': {}
        }
        
        # Ministry mapping for standardization
        self.ministry_codes = {
            'kemenkeu': 'pmk',
            'kemenhub': 'permen-hub',
            'kemen-esdm': 'permen-esdm', 
            'kemendikbud': 'permen-dikbud',
            'kemenkes': 'permen-kes',
            'kemenhan': 'permen-han',
            'bumn': 'permen-bumn'
        }
        
        # Category patterns
        self.patterns = {
            'uu': r'(\d{4})?uu(\d+)|undang[_-]?undang',
            'pp': r'(\d{4})?pp(\d+)|pemerintah',  
            'perpres': r'(\d{4})?perpres(\d+)|presiden',
            'pmk': r'pmk[_-]?(\d+)[_-]?(\d{4})',
            'permenhub': r'(permen)?hub|kemenhub|transportasi',
            'permen_esdm': r'esdm|energi',
            'permen_han': r'pertahanan|han',
            'perda': r'perda|daerah'
        }

    def standardize_filename(self, filename, category):
        """Standardize filename according to rules"""
        base_name = filename.replace('.pdf', '')
        
        # Extract year and number more carefully
        year_matches = re.findall(r'(\d{4})', base_name)
        year = year_matches[0] if year_matches else '2024'
        
        # Extract numbers excluding year
        number_matches = re.findall(r'(\d+)', base_name)
        number = '001'  # default
        
        # Find the right number (not the year)
        for match in number_matches:
            if len(match) <= 3 and match != year:
                number = match.zfill(3)
                break
        
        # Generate standardized name based on category
        if category == 'uu-laws':
            new_name = f"uu-{number}-{year}.pdf"
        elif category == 'pp':
            new_name = f"pp-{number}-{year}.pdf" 
        elif category == 'perpres':
            new_name = f"perpres-{number}-{year}.pdf"
        elif category == 'pmk':
            new_name = f"pmk-{number}-{year}.pdf"
        elif category == 'permenhub':
            new_name = f"permen-hub-{number}-{year}.pdf"
        elif category == 'permen-esdm':
            new_name = f"permen-esdm-{number}-{year}.pdf"
        elif category == 'permen-han':
            new_name = f"permen-han-{number}-{year}.pdf"
        elif category == 'perda':
            new_name = f"perda-{number}-{year}.pdf"
        else:
            # Keep original name if can't categorize
            new_name = filename.lower().replace('_', '-')
            
        return new_name

    def categorize_file(self, filename):
        """Determine category and target directory for file"""
        name_lower = filename.lower()
        
        # Constitutional documents
        if re.search(r'uud|1945|constitutional', name_lower):
            return '01-constitutional/uud-1945', 'uud-1945'
        
        # National laws
        if re.search(self.patterns['uu'], name_lower):
            return '02-national-laws/uu-laws', 'uu-laws'
        if re.search(r'perppu|emergency', name_lower):
            return '02-national-laws/perppu', 'perppu'
        if re.search(r'kuhp|criminal.*code', name_lower):
            return '02-national-laws/kuhp-2023', 'kuhp-2023'
            
        # Government regulations
        if re.search(self.patterns['pp'], name_lower):
            return '03-government-regulations/pp', 'pp'
        if re.search(self.patterns['perpres'], name_lower):
            return '03-government-regulations/perpres', 'perpres'
        if re.search(r'inpres|instruksi', name_lower):
            return '03-government-regulations/inpres', 'inpres'
            
        # Ministerial regulations
        if re.search(self.patterns['pmk'], name_lower):
            return '04-ministerial/by-ministry/kemenkeu', 'pmk'
        if re.search(self.patterns['permenhub'], name_lower):
            return '04-ministerial/by-ministry/kemenhub', 'permenhub'  
        if re.search(self.patterns['permen_esdm'], name_lower):
            return '04-ministerial/by-ministry/kemen-esdm', 'permen-esdm'
        if re.search(self.patterns['permen_han'], name_lower):
            return '04-ministerial/by-ministry/kemenhan', 'permen-han'
        if re.search(r'permen', name_lower):
            return '04-ministerial/by-ministry/other-ministries', 'permen-other'
            
        # Regional regulations
        if re.search(self.patterns['perda'], name_lower):
            return '05-regional/by-province', 'perda'
            
        # Default to specialized if can't categorize
        return '07-specialized/other-institutions', 'other'

    def process_files(self):
        """Main processing function"""
        print("🔄 STARTING COMPREHENSIVE REORGANIZATION...")
        
        # Get all PDF files in root directory (exclude subdirectories for now)
        pdf_files = [f for f in self.base_path.glob('*.pdf') if f.is_file()]
        self.stats['total_files'] = len(pdf_files)
        
        print(f"📊 Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                # Determine category and target directory
                target_dir, category = self.categorize_file(pdf_file.name)
                
                # Standardize filename
                new_filename = self.standardize_filename(pdf_file.name, category)
                
                # Create target directory if it doesn't exist
                target_path = self.base_path / target_dir
                target_path.mkdir(parents=True, exist_ok=True)
                
                # Move and rename file
                new_file_path = target_path / new_filename
                
                # Handle duplicate names
                counter = 1
                original_new_filename = new_filename
                while new_file_path.exists():
                    name_part = original_new_filename.replace('.pdf', '')
                    new_filename = f"{name_part}-{counter:02d}.pdf"
                    new_file_path = target_path / new_filename
                    counter += 1
                
                # Move the file
                shutil.move(str(pdf_file), str(new_file_path))
                
                # Log the operation
                self.filename_mappings.append({
                    'original': pdf_file.name,
                    'new': new_filename,
                    'category': category,
                    'target_directory': target_dir,
                    'timestamp': datetime.now().isoformat()
                })
                
                self.categorization_log.append({
                    'file': pdf_file.name,
                    'category': category,
                    'target': target_dir,
                    'renamed': pdf_file.name != new_filename
                })
                
                # Update stats
                self.stats['moved_files'] += 1
                if pdf_file.name != new_filename:
                    self.stats['renamed_files'] += 1
                
                self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
                
                print(f"✅ {pdf_file.name} → {target_dir}/{new_filename}")
                
            except Exception as e:
                error_msg = f"❌ Error processing {pdf_file.name}: {str(e)}"
                print(error_msg)
                self.error_log.append({
                    'file': pdf_file.name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

    def move_existing_directories(self):
        """Move content from existing organized directories"""
        print("\n🔄 MOVING EXISTING ORGANIZED CONTENT...")
        
        directory_mappings = {
            'uu': '02-national-laws/uu-laws',
            'pp': '03-government-regulations/pp', 
            'perpres': '03-government-regulations/perpres',
            'constitutional': '01-constitutional/uud-1945',
            'esdm': '04-ministerial/by-ministry/kemen-esdm',
            'perda': '05-regional/by-province',
            'permen': '04-ministerial/by-ministry/other-ministries'
        }
        
        for old_dir, new_dir in directory_mappings.items():
            old_path = self.base_path / old_dir
            if old_path.exists() and old_path.is_dir():
                new_path = self.base_path / new_dir
                new_path.mkdir(parents=True, exist_ok=True)
                
                # Move all files from old directory
                for file_path in old_path.glob('*'):
                    if file_path.is_file():
                        target_file = new_path / file_path.name
                        if not target_file.exists():
                            shutil.move(str(file_path), str(target_file))
                            print(f"📁 Moved {old_dir}/{file_path.name} → {new_dir}/{file_path.name}")

    def backup_original_structure(self):
        """Backup original directories to legacy"""
        print("\n💾 BACKING UP ORIGINAL STRUCTURE...")
        
        directories_to_backup = ['hierarchy', 'constitutional', 'esdm', 'others', 
                               'perda', 'permen', 'perpres', 'pp', 'uu']
        
        for dir_name in directories_to_backup:
            source_path = self.base_path / dir_name
            if source_path.exists():
                backup_path = self.base_path / '08-archives' / 'legacy' / f'original-{dir_name}'
                if not backup_path.exists():
                    try:
                        shutil.copytree(str(source_path), str(backup_path))
                        print(f"💾 Backed up {dir_name}/ → 08-archives/legacy/original-{dir_name}/")
                    except Exception as e:
                        print(f"⚠️ Could not backup {dir_name}: {e}")

    def generate_reports(self):
        """Generate comprehensive reports"""
        print("\n📊 GENERATING REPORTS...")
        
        # Filename mapping report
        with open(self.base_path / 'filename_mapping_log.json', 'w', encoding='utf-8') as f:
            json.dump(self.filename_mappings, f, indent=2, ensure_ascii=False)
        
        # Categorization report  
        with open(self.base_path / 'categorization_log.json', 'w', encoding='utf-8') as f:
            json.dump(self.categorization_log, f, indent=2, ensure_ascii=False)
        
        # Statistics report
        with open(self.base_path / 'reorganization_stats.json', 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        # Error log if any errors occurred
        if self.error_log:
            with open(self.base_path / 'reorganization_errors.json', 'w', encoding='utf-8') as f:
                json.dump(self.error_log, f, indent=2, ensure_ascii=False)
        
        print(f"📊 REORGANIZATION COMPLETE!")
        print(f"   • Total files processed: {self.stats['total_files']}")
        print(f"   • Files moved: {self.stats['moved_files']}")
        print(f"   • Files renamed: {self.stats['renamed_files']}")
        print(f"   • Categories created: {len(self.stats['categories'])}")
        if self.error_log:
            print(f"   • Errors encountered: {len(self.error_log)}")

    def run_complete_reorganization(self):
        """Execute the complete reorganization process"""
        self.backup_original_structure()
        self.move_existing_directories()
        self.process_files()
        self.generate_reports()

if __name__ == "__main__":
    reorganizer = LegalDatabaseReorganizer("/root/.openclaw/peraturan-perundang-undangan-pdf")
    reorganizer.run_complete_reorganization()