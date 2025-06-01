#!/bin/bash

output_file="docs/examples.md"
echo "# Exemples DAUPS" > "$output_file"

index=1

find Examples/ -type f -name "*.daups" | sort | while read -r file; do
    echo "Traitement de : $file"
    echo -e "\n## Exemple $index\n" >> "$output_file"
    echo '```daups-docs' >> "$output_file"
    cat "$file" >> "$output_file"
    echo -e '\n```' >> "$output_file"
    ((index++))
done