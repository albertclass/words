#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 input_file [lines]"
    exit 1
fi

input_file=$1
split_lines=50

if [ $# -eq 2 ]; then
    split_lines=$2
fi

line_count=0
total_lines=0
output_file=$((line_count + 1))-$((line_count + $split_lines)).txt

while IFS= read -r line; do
    echo "$line" >> "$output_file"
    line_count=$((line_count + 1))
    if [ $line_count -eq 50 ]; then
        total_lines=$((total_lines + line_count))
        output_file=$((total_lines + 1))-$((total_lines + $split_lines)).txt
        line_count=0
    fi
done < "$input_file"