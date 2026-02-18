#!/bin/bash
# Auto-commit PDFs in batches under 100MB
TOTAL_SIZE=0
FILES=()

for pdf in *.pdf; do
    if [ -f "$pdf" ]; then
        SIZE=$(du -b "$pdf" | cut -f1)
        if [ $((TOTAL_SIZE + SIZE)) -gt 104857600 ]; then  # 100MB
            if [ ${#FILES[@]} -gt 0 ]; then
                echo "Committing batch: ${FILES[*]} (${TOTAL_SIZE} bytes)"
                git add "${FILES[@]}"
                git commit -m "📄 PDF Batch: ${#FILES[@]} files ($(echo $TOTAL_SIZE | awk '{print $1/1024/1024}' | cut -d. -f1)MB)"
                git push origin master
                FILES=()
                TOTAL_SIZE=0
            fi
        fi
        FILES+=("$pdf")
        TOTAL_SIZE=$((TOTAL_SIZE + SIZE))
    fi
done

if [ ${#FILES[@]} -gt 0 ]; then
    echo "Final batch: ${FILES[*]} (${TOTAL_SIZE} bytes)"
    git add "${FILES[@]}"
    git commit -m "📄 PDF Batch: ${#FILES[@]} files ($(echo $TOTAL_SIZE | awk '{print $1/1024/1024}' | cut -d. -f1)MB)"
    git push origin master
fi
