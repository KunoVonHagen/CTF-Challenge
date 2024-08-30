#!/bin/bash

# List of files to commit
files=(
    "images/host.img_part_000"
    "images/host.img_part_001"
    "images/host.img_part_002"
    "images/host.img_part_003"
    "images/host.img_part_004"
    "images/host.img_part_005"
    "images/host.img_part_006"
    "images/host.img_part_007"
    "images/host.img_part_008"
    "images/host.img_part_009"
    "images/host.img_part_010"
    "images/host.img_part_011"
    "images/host.img_part_012"
    "images/host.img_part_013"
    "images/host.img_part_014"
    "images/host.img_part_015"
    "images/host.img_part_016"
    "images/host.img_part_017"
    "images/host.img_part_018"
    "images/monitoring.img_part_000"
    "images/monitoring.img_part_001"
    "images/monitoring.img_part_002"
    "images/monitoring.img_part_003"
    "images/monitoring.img_part_004"
    "images/monitoring.img_part_005"
    "images/monitoring.img_part_006"
    "images/monitoring.img_part_007"
    "images/monitoring.img_part_008"
    "images/monitoring.img_part_009"
    "images/monitoring.img_part_010"
    "images/monitoring.img_part_011"
    "images/monitoring.img_part_012"
    "images/monitoring.img_part_013"
    "images/monitoring.img_part_014"
    "images/monitoring.img_part_015"
    "images/monitoring.img_part_016"
    "images/monitoring.img_part_017"
    "images/monitoring.img_part_018"
    "images/monitoring.img_part_019"
    "images/monitoring.img_part_020"
    "images/monitoring.img_part_021"
    "images/monitoring.img_part_022"
)

# Total number of files
total_files=${#files[@]}

# Loop over each file and commit
for i in "${!files[@]}"; do
    file=${files[$i]}
    index=$((i + 1))
    
    # Stage the file
    git add "$file"
    
    # Commit with the message
    git commit -m "Updating image parts ($index/$total_files)"
    
    # Push the commit
    git push
    
    # Optionally, you might want to check if the push was successful before proceeding
    if [ $? -ne 0 ]; then
        echo "Error pushing commit for $file. Exiting."
        exit 1
    fi
done
