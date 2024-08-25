#!/bin/bash

# Directory containing the tar files
TAR_DIR="images"
# Size of each split chunk (e.g., 100MB)
CHUNK_SIZE=100M

# Function to display an error message and exit
function error_exit {
    echo "[ERROR] $1"
    exit 1
}

# Ensure the directory exists
if [ ! -d "$TAR_DIR" ]; then
    error_exit "Directory '$TAR_DIR' does not exist."
fi

echo "[INFO] Directory '$TAR_DIR' exists. Preparing to split tar files..."

# Flag to track if any tar files were found
tar_files_found=false

# Loop through each tar file in the directory
for tar_file in "$TAR_DIR"/*.tar; do
    if [ -f "$tar_file" ]; then
        # Get the base name of the file (e.g., "frontend.img.tar" becomes "frontend.img")
        base_name=$(basename "$tar_file" .tar)
        
        # Split the file into chunks
        echo "[INFO] Splitting '$tar_file' into chunks of size $CHUNK_SIZE..."
        
        if split -b "$CHUNK_SIZE" -d -a 3 "$tar_file" "$TAR_DIR/${base_name}_part_"; then
            echo "[INFO] Successfully split '$tar_file' into ${base_name}_part_###"
            tar_files_found=true
        else
            error_exit "Failed to split '$tar_file'."
        fi
    fi
done

# If no tar files were found, output a message
if [ "$tar_files_found" = false ]; then
    echo "[WARNING] No tar files found in '$TAR_DIR'."
fi
