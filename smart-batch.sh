#!/bin/bash
# Smart batch commit under 100MB
BATCH_SIZE=0
BATCH_FILES=()
BATCH_NUM=1

for file in $(git status --porcelain | grep "^A " | cut -c4-); do
    if [ -f "$file" ]; then
        FILE_SIZE=$(stat -c%s "$file" 2>/dev/null || echo 0)
        
        # If adding this file would exceed 100MB, commit current batch
        if [ $((BATCH_SIZE + FILE_SIZE)) -gt 100000000 ] && [ ${#BATCH_FILES[@]} -gt 0 ]; then
            echo "Committing batch $BATCH_NUM: ${#BATCH_FILES[@]} files ($(echo $BATCH_SIZE | numfmt --to=iec))"
            git add "${BATCH_FILES[@]}"
            git commit -m "📄 PDF Batch $BATCH_NUM: ${#BATCH_FILES[@]} files ($(echo $BATCH_SIZE | numfmt --to=iec))"
            git push origin master
            
            BATCH_FILES=()
            BATCH_SIZE=0
            ((BATCH_NUM++))
        fi
        
        BATCH_FILES+=("$file")
        BATCH_SIZE=$((BATCH_SIZE + FILE_SIZE))
    fi
done

# Commit final batch
if [ ${#BATCH_FILES[@]} -gt 0 ]; then
    echo "Final batch $BATCH_NUM: ${#BATCH_FILES[@]} files ($(echo $BATCH_SIZE | numfmt --to=iec))"
    git add "${BATCH_FILES[@]}"
    git commit -m "📄 PDF Batch $BATCH_NUM: ${#BATCH_FILES[@]} files ($(echo $BATCH_SIZE | numfmt --to=iec))"
    git push origin master
fi
