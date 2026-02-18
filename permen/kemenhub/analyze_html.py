#!/usr/bin/env python3
"""
Analyze HTML content to understand PDF link patterns
"""
import json
import re

def analyze_regulation_html():
    """Analyze the HTML content captured from regulation pages"""
    
    # Load the metadata
    with open('/root/.openclaw/workspace/kemenhub-backup/kemenhub_metadata.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} regulations in metadata")
    
    # Analyze first few HTML contents
    for i, reg in enumerate(data[:3]):
        print(f"\n=== ANALYZING REGULATION {i+1}: {reg['title']} ===")
        
        if 'html_content' in reg:
            html = reg['html_content']
            print(f"HTML length: {len(html)} characters")
            
            # Look for various PDF patterns
            patterns = [
                r'href="([^"]*\.pdf[^"]*)"',  # Direct PDF links
                r'href="([^"]*pdf[^"]*)"',    # Links containing 'pdf'
                r'href="([^"]*download[^"]*)"',  # Download links
                r'href="([^"]*file[^"]*)"',   # File links
                r'onclick="[^"]*([^"]*\.pdf[^"]*)"',  # PDF in onclick
            ]
            
            print("PDF Pattern Analysis:")
            for j, pattern in enumerate(patterns, 1):
                matches = re.findall(pattern, html, re.IGNORECASE)
                print(f"  Pattern {j}: {len(matches)} matches")
                if matches:
                    for match in matches[:3]:  # Show first 3
                        print(f"    - {match}")
            
            # Look for common download button patterns
            download_patterns = [
                r'<a[^>]*class="[^"]*download[^"]*"[^>]*href="([^"]*)"',
                r'<button[^>]*onclick="[^"]*([^"]*)"[^>]*>.*?download',
                r'href="([^"]*)"[^>]*>.*?unduh',  # "unduh" is "download" in Indonesian
                r'href="([^"]*)"[^>]*>.*?download',
            ]
            
            print("Download Button Analysis:")
            for j, pattern in enumerate(download_patterns, 1):
                matches = re.findall(pattern, html, re.IGNORECASE)
                print(f"  Button Pattern {j}: {len(matches)} matches")
                if matches:
                    for match in matches[:3]:
                        print(f"    - {match}")
            
            # Look for any links at all
            all_links = re.findall(r'href="([^"]*)"', html)
            print(f"Total links found: {len(all_links)}")
            
            # Check if HTML is actually complete
            if '<html' in html and '</html>' in html:
                print("Complete HTML page detected")
            else:
                print("Incomplete HTML or fragment")
                
            # Print a snippet of the HTML around potential download areas
            download_section = re.search(r'.{0,200}(download|unduh|pdf).{0,200}', html, re.IGNORECASE)
            if download_section:
                print("HTML snippet around download area:")
                print(download_section.group(0))
        else:
            print("No HTML content found")
    
    print("\n=== SUMMARY ===")
    html_count = sum(1 for reg in data if 'html_content' in reg)
    print(f"Regulations with HTML content: {html_count}/{len(data)}")

if __name__ == "__main__":
    analyze_regulation_html()