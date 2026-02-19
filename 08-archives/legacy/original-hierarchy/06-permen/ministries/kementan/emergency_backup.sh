#!/bin/bash
# EMERGENCY KEMENTAN REGULATION BACKUP SYSTEM
# NO ANALYSIS - PURE DATA CONVERSION ONLY!

set -e  # Exit on any error

# Configuration
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PDF_DIR="$BASE_DIR/pdf-sources"
MARKDOWN_DIR="$BASE_DIR/markdown-output"  
LOG_DIR="$BASE_DIR/logs"
METADATA_DIR="$BASE_DIR/metadata"

# Create log file with timestamp
LOG_FILE="$LOG_DIR/backup_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check dependencies
check_dependencies() {
    log "🔍 Checking dependencies..."
    
    local missing_deps=()
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Check for PDF tools
    if ! command -v pdftotext &> /dev/null; then
        log "⚠️  pdftotext not found - will try Python pdfplumber"
    fi
    
    # Check Python packages
    if ! python3 -c "import pdfplumber" &> /dev/null; then
        log "⚠️  pdfplumber not installed - install with: pip install pdfplumber"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log "❌ Missing dependencies: ${missing_deps[*]}"
        log "📦 Install missing packages and retry"
        exit 1
    fi
    
    log "✅ All dependencies available"
}

# Create directory structure
setup_directories() {
    log "📁 Setting up directory structure..."
    
    mkdir -p "$PDF_DIR" "$MARKDOWN_DIR" "$LOG_DIR" "$METADATA_DIR"
    
    log "✅ Directory structure created:"
    log "   📁 PDF Sources: $PDF_DIR"
    log "   📝 Markdown Output: $MARKDOWN_DIR"  
    log "   📊 Logs: $LOG_DIR"
    log "   🗃️  Metadata: $METADATA_DIR"
}

# Count files function
count_files() {
    local dir="$1"
    local pattern="$2"
    
    if [ -d "$dir" ]; then
        find "$dir" -name "$pattern" 2>/dev/null | wc -l
    else
        echo "0"
    fi
}

# Scan for PDF files
scan_pdfs() {
    local pdf_count
    pdf_count=$(count_files "$PDF_DIR" "*.pdf")
    
    log "🔍 Scanning for PDF files..."
    log "📄 Found $pdf_count PDF files in $PDF_DIR"
    
    if [ "$pdf_count" -eq 0 ]; then
        log "⚠️  No PDF files found!"
        log "📥 To add PDF files:"
        log "   1. Download Permen Kementan PDFs from official sources"  
        log "   2. Place them in: $PDF_DIR"
        log "   3. Run this script again"
        return 1
    fi
    
    # List PDF files
    log "📄 PDF Files found:"
    find "$PDF_DIR" -name "*.pdf" -type f | while read -r file; do
        local size=$(du -h "$file" | cut -f1)
        local basename=$(basename "$file")
        log "   • $basename ($size)"
    done
    
    return 0
}

# Convert PDFs to Markdown
convert_pdfs() {
    log "🔄 Starting PDF to Markdown conversion..."
    log "⚡ EMERGENCY MODE: Maximum speed conversion"
    log "📝 FORMAT: Raw regulation text only - NO ANALYSIS"
    
    # Run the Python conversion script
    if python3 "$BASE_DIR/scripts/pdf_to_markdown.py" batch; then
        local converted_count
        converted_count=$(count_files "$MARKDOWN_DIR" "*.md")
        log "✅ Conversion completed: $converted_count markdown files generated"
    else
        log "❌ Conversion failed! Check logs for details"
        return 1
    fi
}

# Generate metadata
generate_metadata() {
    log "🗃️  Generating metadata..."
    
    local metadata_file="$METADATA_DIR/backup_metadata_$(date +%Y%m%d_%H%M%S).json"
    
    # Count statistics
    local pdf_count markdown_count
    pdf_count=$(count_files "$PDF_DIR" "*.pdf")
    markdown_count=$(count_files "$MARKDOWN_DIR" "*.md")
    
    # Calculate sizes
    local pdf_size markdown_size
    pdf_size=$(du -sb "$PDF_DIR" 2>/dev/null | cut -f1 || echo "0")
    markdown_size=$(du -sb "$MARKDOWN_DIR" 2>/dev/null | cut -f1 || echo "0")
    
    # Create metadata JSON
    cat > "$metadata_file" << EOF
{
    "backup_info": {
        "timestamp": "$(date -Iseconds)",
        "mission": "EMERGENCY KEMENTAN REGULATION BACKUP",
        "status": "COMPLETED",
        "format": "RAW_REGULATION_TEXT_ONLY"
    },
    "statistics": {
        "pdf_files": $pdf_count,
        "markdown_files": $markdown_count,
        "pdf_size_bytes": $pdf_size,
        "markdown_size_bytes": $markdown_size,
        "conversion_rate": "$(echo "scale=2; $markdown_count * 100 / $pdf_count" | bc 2>/dev/null || echo "N/A")%"
    },
    "directories": {
        "pdf_sources": "$PDF_DIR",
        "markdown_output": "$MARKDOWN_DIR",
        "logs": "$LOG_DIR",
        "metadata": "$METADATA_DIR"
    }
}
EOF
    
    log "📋 Metadata saved to: $metadata_file"
}

# Generate final report
generate_report() {
    log "📊 EMERGENCY BACKUP FINAL REPORT"
    log "================================="
    
    local pdf_count markdown_count
    pdf_count=$(count_files "$PDF_DIR" "*.pdf") 
    markdown_count=$(count_files "$MARKDOWN_DIR" "*.md")
    
    log "🚨 MISSION STATUS: EMERGENCY BACKUP COMPLETED"
    log "📄 PDF FILES PROCESSED: $pdf_count"
    log "📝 MARKDOWN FILES GENERATED: $markdown_count"
    log "🔄 CONVERSION SUCCESS: $(echo "scale=1; $markdown_count * 100 / $pdf_count" | bc 2>/dev/null || echo "N/A")%"
    
    # Show largest files
    log ""
    log "📊 LARGEST PDF FILES:"
    find "$PDF_DIR" -name "*.pdf" -type f -exec du -h {} + 2>/dev/null | sort -hr | head -5 | while read -r line; do
        log "   $line"
    done
    
    log ""
    log "📊 LARGEST MARKDOWN FILES:"  
    find "$MARKDOWN_DIR" -name "*.md" -type f -exec du -h {} + 2>/dev/null | sort -hr | head -5 | while read -r line; do
        log "   $line"
    done
    
    log ""
    log "✅ EMERGENCY DATA PRESERVATION MISSION COMPLETED"
    log "📁 BACKUP LOCATION: $BASE_DIR"
    log "📋 LOG FILE: $LOG_FILE"
}

# Main execution
main() {
    log "🚨 EMERGENCY KEMENTAN REGULATION BACKUP SYSTEM STARTING"
    log "========================================================"
    log "🎯 MISSION: Emergency backup of Agriculture regulations"
    log "⚡ MODE: NO ANALYSIS - PURE DATA CONVERSION ONLY"
    log "🚀 TARGET: Maximum speed regulation preservation"
    
    # Setup
    check_dependencies
    setup_directories
    
    # Process PDFs
    if scan_pdfs; then
        convert_pdfs
        generate_metadata
        generate_report
        
        log ""
        log "🎉 EMERGENCY BACKUP MISSION ACCOMPLISHED!"
        log "📂 Results available in: $BASE_DIR"
        
        # Run monitoring scan
        log ""
        log "📊 Running final monitoring scan..."
        if [ -f "$BASE_DIR/scripts/emergency_monitor.py" ]; then
            python3 "$BASE_DIR/scripts/emergency_monitor.py" scan
        fi
        
    else
        log ""
        log "⏳ BACKUP SYSTEM READY - WAITING FOR PDF FILES"
        log "📥 Add PDF files to: $PDF_DIR"
        log "🔄 Then run: $0"
    fi
}

# Run main function
main "$@"