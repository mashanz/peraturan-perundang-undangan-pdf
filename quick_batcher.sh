#!/bin/bash
set -e

echo "🚀 Starting Indonesian Legal Database Batch Commit & Push"

# Initialize counters
batch_count=0
total_files=0

# Function to process a batch
process_batch() {
    local files=("$@")
    local batch_size=${#files[@]}
    
    if [ $batch_size -eq 0 ]; then
        return
    fi
    
    ((batch_count++))
    ((total_files += batch_size))
    
    echo ""
    echo "🔄 Processing Batch $batch_count: $batch_size files"
    
    # Add files to git
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            git add "$file" || echo "⚠️ Warning: Could not add $file"
        fi
    done
    
    # Check if anything was actually staged
    if [ -n "$(git diff --cached --name-only)" ]; then
        # Commit
        git commit -m "Batch $batch_count: Add $batch_size Indonesian legal documents

- Systematic organization of Indonesian legal framework
- PDF documents for legal research and compliance
- Categorized by document type: UU, PP, Perpres, Permen, Perda
- Repository: Indonesian Legal Database Project"
        
        echo "✅ Committed batch $batch_count"
        
        # Push immediately
        if git push origin master; then
            echo "🚀 Pushed batch $batch_count successfully"
        else
            echo "❌ Failed to push batch $batch_count"
            return 1
        fi
        
        # Brief pause to be nice to GitHub
        sleep 2
    else
        echo "⚠️ No files staged for batch $batch_count"
    fi
}

# Get all untracked files
mapfile -t all_files < <(git ls-files --others --exclude-standard)
total_untracked=${#all_files[@]}

echo "📊 Found $total_untracked untracked files"

if [ $total_untracked -eq 0 ]; then
    echo "✅ No files to process!"
    exit 0
fi

# Process files in batches of 25 to keep things manageable
batch_size=25
batch_files=()

for file in "${all_files[@]}"; do
    batch_files+=("$file")
    
    # When batch is full, process it
    if [ ${#batch_files[@]} -eq $batch_size ]; then
        process_batch "${batch_files[@]}"
        batch_files=()
    fi
done

# Process remaining files
if [ ${#batch_files[@]} -gt 0 ]; then
    process_batch "${batch_files[@]}"
fi

echo ""
echo "🎉 PDF Repository Processing Complete!"
echo "✅ Processed $batch_count batches"
echo "📊 Total files added: $total_files"

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -f batch_plan.json batch_analyzer.py batch_processor.py simple_batcher.py quick_batcher.sh

echo "🎯 PDF Repository mission accomplished!"