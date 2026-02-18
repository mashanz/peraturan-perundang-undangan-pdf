#!/bin/bash
# KEMKES EMERGENCY BACKUP CONVERTER
# Pure data conversion - NO analysis allowed

set -e

DOWNLOAD_DIR="kemkes-pdfs"
OUTPUT_DIR="kemkes-markdown"

# Create directories
mkdir -p "$DOWNLOAD_DIR" "$OUTPUT_DIR"

# Function to convert PDF to clean markdown
convert_pdf_to_md() {
    local pdf_file="$1"
    local output_file="$2"
    
    echo "Converting: $pdf_file -> $output_file"
    
    # Extract text using pdftotext (when available)
    if command -v pdftotext &> /dev/null; then
        pdftotext -layout -nopgbrk "$pdf_file" - | \
        sed 's/\f//g' | \
        sed '/^$/N;/^\n$/d' > "$output_file"
    else
        echo "# PDF CONVERSION PLACEHOLDER" > "$output_file"
        echo "Source: $pdf_file" >> "$output_file"
        echo "Status: Awaiting pdftotext installation" >> "$output_file"
    fi
}

# Function to download and convert a single document
process_document() {
    local url="$1"
    local filename="$2"
    
    echo "Processing: $filename"
    local pdf_path="$DOWNLOAD_DIR/$filename"
    local md_path="$OUTPUT_DIR/${filename%.*}.md"
    
    # Download PDF
    if wget -q -O "$pdf_path" "$url"; then
        convert_pdf_to_md "$pdf_path" "$md_path"
        echo "SUCCESS: $filename converted"
        return 0
    else
        echo "FAILED: Could not download $filename"
        return 1
    fi
}

# Function to process multiple documents in parallel
batch_process() {
    local url_list="$1"
    local max_parallel=5
    
    if [[ ! -f "$url_list" ]]; then
        echo "ERROR: URL list file not found: $url_list"
        return 1
    fi
    
    # Read URLs and process in parallel
    while IFS= read -r line; do
        if [[ ! "$line" =~ ^# ]] && [[ -n "$line" ]]; then
            url=$(echo "$line" | cut -d' ' -f1)
            filename=$(echo "$line" | cut -d' ' -f2)
            
            # Run in background with job control
            {
                process_document "$url" "$filename"
            } &
            
            # Limit parallel jobs
            while (( $(jobs -r | wc -l) >= max_parallel )); do
                sleep 0.1
            done
        fi
    done < "$url_list"
    
    # Wait for all background jobs to complete
    wait
    
    echo "Batch processing complete!"
}

# Main execution
if [[ $# -eq 0 ]]; then
    echo "KEMKES Emergency Backup Converter"
    echo "Usage: $0 <command> [args]"
    echo "Commands:"
    echo "  convert <pdf_file> [output_file]  - Convert single PDF"
    echo "  batch <url_list_file>             - Process batch from file"
    echo "  test                              - Test conversion system"
    exit 1
fi

case "$1" in
    "convert")
        if [[ -z "$2" ]]; then
            echo "ERROR: PDF file required"
            exit 1
        fi
        output_file="${3:-${2%.*}.md}"
        convert_pdf_to_md "$2" "$output_file"
        ;;
    "batch")
        if [[ -z "$2" ]]; then
            echo "ERROR: URL list file required"
            exit 1
        fi
        batch_process "$2"
        ;;
    "test")
        echo "Testing conversion system..."
        echo "Tools available:"
        echo "- wget: $(command -v wget || echo 'NOT FOUND')"
        echo "- pdftotext: $(command -v pdftotext || echo 'NOT FOUND')"
        echo "- pandoc: $(command -v pandoc || echo 'NOT FOUND')"
        echo ""
        echo "Directory structure:"
        ls -la "$DOWNLOAD_DIR" "$OUTPUT_DIR" 2>/dev/null || echo "Directories will be created on first run"
        ;;
    *)
        echo "ERROR: Unknown command '$1'"
        exit 1
        ;;
esac