#!/usr/bin/env python3
"""
PERMEN Parser - Extract ministerial regulations from sitemap
Part of the mass PERMEN download operation
"""
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import os
import sys

def extract_permen_urls(sitemap_path):
    """Extract all PERMEN URLs from the sitemap XML file"""
    permen_urls = []
    ministry_stats = {}
    
    print(f"Parsing sitemap from: {sitemap_path}")
    
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix XML structure - remove outer response tags and unescape inner XML
    content = content.replace('&lt;', '<').replace('&gt;', '>')
    start = content.find('<urlset')
    end = content.rfind('</urlset>') + 9
    xml_content = content[start:end]
    
    try:
        root = ET.fromstring(xml_content)
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = root.findall('.//sitemap:url', namespace)
        print(f"Total URLs found in sitemap: {len(urls)}")
        
        for url_elem in urls:
            loc_elem = url_elem.find('sitemap:loc', namespace)
            if loc_elem is not None:
                url = loc_elem.text
                
                # Check if this is a PERMEN URL
                if is_permen_url(url):
                    ministry = extract_ministry_from_url(url)
                    permen_urls.append({
                        'url': url,
                        'ministry': ministry,
                        'filename': generate_filename_from_url(url)
                    })
                    
                    # Track ministry statistics
                    if ministry in ministry_stats:
                        ministry_stats[ministry] += 1
                    else:
                        ministry_stats[ministry] = 1
    
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return [], {}
    
    print(f"Total PERMEN URLs found: {len(permen_urls)}")
    print("Ministry breakdown:")
    for ministry, count in sorted(ministry_stats.items()):
        print(f"  {ministry}: {count} regulations")
    
    return permen_urls, ministry_stats

def is_permen_url(url):
    """Check if URL is a ministerial regulation (PERMEN)"""
    # Match patterns like permenkes, permenkeu, permenhub, etc.
    permen_patterns = [
        r'/permen[a-zA-Z]+-',  # permenkes, permenkeu, etc.
        r'/peraturan-menteri-',  # full form
        r'/pm[a-zA-Z]+-',  # pmk (peraturan menteri keuangan), etc.
        r'/kepmen[a-zA-Z]+-',  # keputusan menteri
        r'/permendag-',  # ministry of trade
        r'/permendikbud-',  # ministry of education
        r'/permenhub-',  # ministry of transportation
        r'/permentan-',  # ministry of agriculture
        r'/permenkes-',  # ministry of health
        r'/permenkominfo-',  # ministry of communication
        r'/permen-[a-zA-Z]+',  # generic permen format
    ]
    
    for pattern in permen_patterns:
        if re.search(pattern, url):
            return True
    
    return False

def extract_ministry_from_url(url):
    """Extract ministry code from PERMEN URL"""
    url_lower = url.lower()
    
    # Ministry mappings
    ministry_map = {
        'permenkes': 'kemkes',
        'pmk': 'kemenkeu',
        'permenkeu': 'kemenkeu',
        'permenhub': 'kemenhub',
        'permentan': 'kementan',
        'permendikbud': 'kemdikbud',
        'permendikbudristek': 'kemdikbud',
        'permendag': 'kemendag',
        'permenkominfo': 'kemkominfo',
        'permenkomdigi': 'kemkomdigi',
        'permen-esdm': 'esdm',
        'permenesdm': 'esdm',
        'permen-klhk': 'klhk',
        'permenklhk': 'klhk',
        'permen-pppa': 'kemenpppa',
        'permenpppa': 'kemenpppa',
        'kepmenkes': 'kemkes',
        'kepmenkeu': 'kemenkeu',
        'kepmenhub': 'kemenhub',
        'kepmentan': 'kementan',
        'kepmendikbud': 'kemdikbud',
        'kepmendag': 'kemendag',
        'kepmenesdm': 'esdm',
        'kepmenklhk': 'klhk',
    }
    
    for key, ministry in ministry_map.items():
        if key in url_lower:
            return ministry
    
    # Try to extract from generic patterns
    if 'permen-' in url_lower:
        parts = url_lower.split('permen-')
        if len(parts) > 1:
            ministry_part = parts[1].split('-')[0]
            return ministry_part
    
    return 'unknown'

def generate_filename_from_url(url):
    """Generate PDF filename from regulation URL"""
    # Extract the regulation identifier from URL
    path = urlparse(url).path
    if path.startswith('/id/'):
        regulation_id = path[4:]  # Remove '/id/' prefix
        return f"{regulation_id}.pdf"
    
    return None

def write_batch_files(permen_urls, batch_size=500):
    """Write URLs to batch files for processing"""
    batch_dir = "/root/.openclaw/peraturan-perundang-undangan-pdf/permen_batches"
    os.makedirs(batch_dir, exist_ok=True)
    
    batch_num = 1
    batch_files = []
    
    for i in range(0, len(permen_urls), batch_size):
        batch = permen_urls[i:i+batch_size]
        batch_file = f"{batch_dir}/batch_{batch_num:04d}.txt"
        
        with open(batch_file, 'w') as f:
            for item in batch:
                f.write(f"{item['url']}|{item['ministry']}|{item['filename']}\n")
        
        batch_files.append(batch_file)
        print(f"Created batch {batch_num}: {len(batch)} URLs -> {batch_file}")
        batch_num += 1
    
    return batch_files

if __name__ == "__main__":
    sitemap_path = "/root/.openclaw/workspace/sitemap.xml"
    
    if not os.path.exists(sitemap_path):
        print(f"Error: Sitemap file not found at {sitemap_path}")
        sys.exit(1)
    
    print("=== PERMEN Mass Download Parser ===")
    print("Extracting ministerial regulations from peraturan.go.id sitemap...")
    
    # Parse sitemap and extract PERMEN URLs
    permen_urls, ministry_stats = extract_permen_urls(sitemap_path)
    
    if not permen_urls:
        print("No PERMEN URLs found in sitemap!")
        sys.exit(1)
    
    # Create batch files for download processing
    batch_files = write_batch_files(permen_urls, batch_size=500)
    
    # Write summary report
    summary_file = "/root/.openclaw/peraturan-perundang-undangan-pdf/permen_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"PERMEN Mass Download Summary\n")
        f.write(f"Generated: {os.popen('date').read().strip()}\n")
        f.write(f"Total PERMEN URLs: {len(permen_urls)}\n")
        f.write(f"Number of batches: {len(batch_files)}\n\n")
        f.write("Ministry breakdown:\n")
        for ministry, count in sorted(ministry_stats.items()):
            f.write(f"  {ministry}: {count} regulations\n")
        f.write(f"\nBatch files created:\n")
        for batch_file in batch_files:
            f.write(f"  {batch_file}\n")
    
    print(f"\nSummary written to: {summary_file}")
    print(f"Ready to process {len(batch_files)} batch files")
    print("Next: Run download script with batch processing")