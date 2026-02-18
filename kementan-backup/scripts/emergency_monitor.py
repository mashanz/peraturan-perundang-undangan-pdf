#!/usr/bin/env python3
"""
EMERGENCY KEMENTAN BACKUP MONITORING SYSTEM
Real-time status monitoring for regulation backup process
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class BackupMonitor:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.pdf_dir = self.base_dir / "pdf-sources"
        self.markdown_dir = self.base_dir / "markdown-output"
        self.log_dir = self.base_dir / "logs"
        self.stats_file = self.base_dir / "backup_stats.json"
    
    def scan_directories(self):
        """Scan all directories and collect statistics"""
        stats = {
            "scan_time": datetime.now().isoformat(),
            "pdf_files": [],
            "markdown_files": [],
            "conversion_status": {},
            "summary": {}
        }
        
        # Scan PDF files
        if self.pdf_dir.exists():
            for pdf_file in self.pdf_dir.glob("*.pdf"):
                stats["pdf_files"].append({
                    "filename": pdf_file.name,
                    "size_mb": round(pdf_file.stat().st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat()
                })
        
        # Scan Markdown files
        if self.markdown_dir.exists():
            for md_file in self.markdown_dir.glob("*.md"):
                stats["markdown_files"].append({
                    "filename": md_file.name,
                    "size_kb": round(md_file.stat().st_size / 1024, 2),
                    "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                })
        
        # Calculate conversion status
        pdf_names = {f["filename"].replace(".pdf", "") for f in stats["pdf_files"]}
        md_names = {f["filename"].replace(".md", "") for f in stats["markdown_files"]}
        
        for pdf_name in pdf_names:
            # Try to match with markdown files (allowing for naming variations)
            converted = any(pdf_name in md_name or md_name in pdf_name for md_name in md_names)
            stats["conversion_status"][pdf_name] = "CONVERTED" if converted else "PENDING"
        
        # Summary statistics
        stats["summary"] = {
            "total_pdfs": len(stats["pdf_files"]),
            "total_markdowns": len(stats["markdown_files"]),
            "conversion_rate": f"{len([s for s in stats['conversion_status'].values() if s == 'CONVERTED'])}/{len(stats['conversion_status'])}",
            "total_pdf_size_mb": sum(f["size_mb"] for f in stats["pdf_files"]),
            "total_markdown_size_kb": sum(f["size_kb"] for f in stats["markdown_files"])
        }
        
        return stats
    
    def save_stats(self, stats):
        """Save statistics to JSON file"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    
    def print_status_report(self, stats):
        """Print formatted status report"""
        print("\n" + "="*60)
        print("🚨 EMERGENCY KEMENTAN BACKUP STATUS REPORT")
        print("="*60)
        
        print(f"⏰ SCAN TIME: {stats['scan_time']}")
        print(f"📁 PDF FILES: {stats['summary']['total_pdfs']} ({stats['summary']['total_pdf_size_mb']:.1f} MB)")
        print(f"📝 MARKDOWN FILES: {stats['summary']['total_markdowns']} ({stats['summary']['total_markdown_size_kb']:.1f} KB)")
        print(f"✅ CONVERSION RATE: {stats['summary']['conversion_rate']}")
        
        # Show conversion status
        if stats["conversion_status"]:
            print(f"\n📊 CONVERSION STATUS:")
            for filename, status in stats["conversion_status"].items():
                status_icon = "✅" if status == "CONVERTED" else "⏳"
                print(f"   {status_icon} {filename}: {status}")
        
        # Recent files
        if stats["pdf_files"]:
            print(f"\n📄 RECENT PDF FILES:")
            for pdf in sorted(stats["pdf_files"], key=lambda x: x["modified"], reverse=True)[:5]:
                print(f"   • {pdf['filename']} ({pdf['size_mb']:.1f} MB)")
        
        if stats["markdown_files"]:
            print(f"\n📝 RECENT MARKDOWN FILES:")
            for md in sorted(stats["markdown_files"], key=lambda x: x["modified"], reverse=True)[:5]:
                print(f"   • {md['filename']} ({md['size_kb']:.1f} KB)")
        
        print("\n" + "="*60)
    
    def monitor_continuous(self, interval=30):
        """Continuous monitoring with specified interval"""
        print("🚨 Starting Emergency Backup Monitoring System...")
        print(f"📊 Monitoring interval: {interval} seconds")
        
        try:
            while True:
                stats = self.scan_directories()
                self.save_stats(stats)
                self.print_status_report(stats)
                
                print(f"\n⏳ Next scan in {interval} seconds... (Press Ctrl+C to stop)")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            print("📊 Final statistics saved to:", self.stats_file)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python emergency_monitor.py <command> [options]")
        print("Commands:")
        print("  scan        - Single scan and report")
        print("  monitor     - Continuous monitoring (default 30s interval)")
        print("  monitor X   - Continuous monitoring with X second interval")
        sys.exit(1)
    
    base_dir = Path(__file__).parent.parent
    monitor = BackupMonitor(base_dir)
    
    command = sys.argv[1]
    
    if command == "scan":
        stats = monitor.scan_directories()
        monitor.save_stats(stats)
        monitor.print_status_report(stats)
        
    elif command == "monitor":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor.monitor_continuous(interval)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()