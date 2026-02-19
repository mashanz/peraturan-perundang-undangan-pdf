#!/usr/bin/env python3
"""
PDF Validation Script
Validates all downloaded PDFs for corruption, size, and structure
Part of the Quality Assurance process for regulatory documents
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime
import subprocess

# Configuration
BASE_DIR = Path("/root/.openclaw/peraturan-perundang-undangan-pdf")
MIN_PDF_SIZE = 1000  # bytes
EXPECTED_MIN_SIZE = 10000  # Most PDFs should be larger than 10KB

def validate_pdf_structure(file_path):
    """Use file command to validate PDF structure"""
    try:
        result = subprocess.run(['file', str(file_path)], 
                              capture_output=True, text=True, timeout=5)
        output = result.stdout.lower()
        
        if 'pdf document' in output:
            return True, "Valid PDF structure"
        elif 'empty' in output:
            return False, "Empty file"
        else:
            return False, f"Invalid file type: {output.strip()}"
    except Exception as e:
        return False, f"File validation error: {e}"

def validate_pdf_header(file_path):
    """Check PDF header manually"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(10)
            if header.startswith(b'%PDF-'):
                version = header[5:8].decode('ascii', errors='ignore')
                return True, f"Valid PDF header (version {version})"
            else:
                return False, f"Invalid PDF header: {header[:10]}"
    except Exception as e:
        return False, f"Header validation error: {e}"

def analyze_file(file_path):
    """Comprehensive file analysis"""
    if not file_path.exists():
        return {
            "exists": False,
            "error": "File does not exist",
            "is_valid": False,
            "has_warnings": False,
            "size": 0
        }
    
    # Basic file stats
    stat = file_path.stat()
    size = stat.st_size
    
    analysis = {
        "path": str(file_path),
        "name": file_path.name,
        "size": size,
        "exists": True,
        "size_category": "empty" if size == 0 else "tiny" if size < MIN_PDF_SIZE else "small" if size < EXPECTED_MIN_SIZE else "normal",
        "warnings": [],
        "errors": []
    }
    
    # Size validation
    if size == 0:
        analysis["errors"].append("File is empty (0 bytes)")
        analysis["is_valid"] = False
        analysis["has_warnings"] = False
        return analysis
    elif size < MIN_PDF_SIZE:
        analysis["errors"].append(f"File too small ({size} bytes, minimum {MIN_PDF_SIZE})")
        analysis["is_valid"] = False
        analysis["has_warnings"] = False
        return analysis
    elif size < EXPECTED_MIN_SIZE:
        analysis["warnings"].append(f"File smaller than expected ({size} bytes)")
    
    # Header validation
    header_valid, header_msg = validate_pdf_header(file_path)
    if not header_valid:
        analysis["errors"].append(f"Header validation failed: {header_msg}")
    else:
        analysis["header_valid"] = True
        analysis["header_info"] = header_msg
    
    # Structure validation using file command
    struct_valid, struct_msg = validate_pdf_structure(file_path)
    if not struct_valid:
        analysis["errors"].append(f"Structure validation failed: {struct_msg}")
    else:
        analysis["structure_valid"] = True
        analysis["structure_info"] = struct_msg
    
    # Overall validity
    analysis["is_valid"] = len(analysis["errors"]) == 0
    analysis["has_warnings"] = len(analysis["warnings"]) > 0
    
    return analysis

def scan_directory(directory, pattern="*.pdf"):
    """Scan directory for PDF files and validate them"""
    results = {
        "directory": str(directory),
        "scan_time": datetime.now().isoformat(),
        "files": [],
        "summary": {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "empty_files": 0,
            "tiny_files": 0,
            "small_files": 0,
            "total_size": 0,
            "warnings": 0
        }
    }
    
    if not directory.exists():
        results["error"] = "Directory does not exist"
        return results
    
    # Find all PDF files recursively
    pdf_files = list(directory.rglob(pattern))
    results["summary"]["total_files"] = len(pdf_files)
    
    print(f"Scanning {len(pdf_files)} PDF files in {directory}...")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(pdf_files)} ({i/len(pdf_files)*100:.1f}%)")
        
        analysis = analyze_file(pdf_file)
        results["files"].append(analysis)
        
        # Update summary
        if analysis["exists"]:
            results["summary"]["total_size"] += analysis["size"]
            
            if analysis["size"] == 0:
                results["summary"]["empty_files"] += 1
            elif analysis["size_category"] == "tiny":
                results["summary"]["tiny_files"] += 1
            elif analysis["size_category"] == "small":
                results["summary"]["small_files"] += 1
            
            if analysis["is_valid"]:
                results["summary"]["valid_files"] += 1
            else:
                results["summary"]["invalid_files"] += 1
            
            if analysis["has_warnings"]:
                results["summary"]["warnings"] += 1
    
    # Calculate additional stats
    if results["summary"]["total_files"] > 0:
        results["summary"]["validity_rate"] = (
            results["summary"]["valid_files"] / results["summary"]["total_files"] * 100
        )
        results["summary"]["average_size"] = (
            results["summary"]["total_size"] / results["summary"]["total_files"]
        )
    
    return results

def generate_report(results, output_file):
    """Generate detailed validation report"""
    summary = results["summary"]
    
    report_lines = [
        "PDF VALIDATION REPORT",
        "=" * 50,
        f"Directory: {results['directory']}",
        f"Scan Time: {results['scan_time']}",
        "",
        "SUMMARY:",
        f"  Total Files: {summary['total_files']:,}",
        f"  Valid Files: {summary['valid_files']:,} ({summary.get('validity_rate', 0):.1f}%)",
        f"  Invalid Files: {summary['invalid_files']:,}",
        f"  Empty Files: {summary['empty_files']:,}",
        f"  Tiny Files (<{MIN_PDF_SIZE}B): {summary['tiny_files']:,}",
        f"  Small Files (<{EXPECTED_MIN_SIZE}B): {summary['small_files']:,}",
        f"  Files with Warnings: {summary['warnings']:,}",
        f"  Total Size: {summary['total_size']:,} bytes ({summary['total_size']/1024/1024:.1f} MB)",
        f"  Average Size: {summary.get('average_size', 0):.0f} bytes",
        "",
        "ISSUES FOUND:",
    ]
    
    # List problematic files
    empty_files = [f for f in results["files"] if f.get("size", 0) == 0]
    invalid_files = [f for f in results["files"] if not f.get("is_valid", False) and f.get("size", 0) > 0]
    warning_files = [f for f in results["files"] if f.get("has_warnings", False)]
    
    if empty_files:
        report_lines.append(f"\nEMPTY FILES ({len(empty_files)}):")
        for f in empty_files[:50]:  # Limit to first 50
            report_lines.append(f"  - {f['name']}")
        if len(empty_files) > 50:
            report_lines.append(f"  ... and {len(empty_files) - 50} more")
    
    if invalid_files:
        report_lines.append(f"\nINVALID FILES ({len(invalid_files)}):")
        for f in invalid_files[:50]:  # Limit to first 50
            errors = '; '.join(f.get('errors', []))
            report_lines.append(f"  - {f['name']} ({f.get('size', 0)} bytes): {errors}")
        if len(invalid_files) > 50:
            report_lines.append(f"  ... and {len(invalid_files) - 50} more")
    
    if warning_files:
        report_lines.append(f"\nFILES WITH WARNINGS ({len(warning_files)}):")
        for f in warning_files[:20]:  # Limit to first 20
            warnings = '; '.join(f.get('warnings', []))
            report_lines.append(f"  - {f['name']} ({f.get('size', 0)} bytes): {warnings}")
        if len(warning_files) > 20:
            report_lines.append(f"  ... and {len(warning_files) - 20} more")
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Report written to: {output_file}")
    print("\nSUMMARY:")
    print(f"  Total: {summary['total_files']:,} files")
    print(f"  Valid: {summary['valid_files']:,} ({summary.get('validity_rate', 0):.1f}%)")
    print(f"  Issues: {summary['invalid_files'] + summary['empty_files']:,}")

def main():
    """Main validation process"""
    print("PDF Validation Script Starting...")
    
    # Validate main directory
    main_results = scan_directory(BASE_DIR)
    
    # Save detailed results as JSON
    with open(BASE_DIR / "validation_results.json", 'w') as f:
        json.dump(main_results, f, indent=2)
    
    # Generate human-readable report
    generate_report(main_results, BASE_DIR / "validation_report.txt")
    
    print("\nValidation complete!")
    
    # Also scan PERDA directory specifically
    perda_dir = BASE_DIR / "perda"
    if perda_dir.exists():
        print("\nValidating PERDA directory specifically...")
        perda_results = scan_directory(perda_dir)
        
        with open(perda_dir / "perda_validation_results.json", 'w') as f:
            json.dump(perda_results, f, indent=2)
        
        generate_report(perda_results, perda_dir / "perda_validation_report.txt")

if __name__ == "__main__":
    main()