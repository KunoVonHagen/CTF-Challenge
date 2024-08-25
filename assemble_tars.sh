#!/bin/bash

# Directory containing the split files
TAR_DIR="images"

# Function to display an error message and exit
function error_exit {
    echo "[ERROR] $1"
    exit 1
}

# Ensure the directory exists
if [ ! -d "$TAR_DIR" ]; then
    error_exit "Directory '$TAR_DIR' does not exist."
fi

echo "[INFO] Directory '$TAR_DIR' exists. Reassembling split tar files..."

# Loop through the unique base names of the split files
for prefix in $(ls "$TAR_DIR"/*_part_* 2>/dev/null | sed 's/_part_.*//' | uniq); do
    # Construct the tar filename
    tar_file="${prefix##*/}.tar"

    # Reassemble the chunks into a tar file
    if cat ${prefix}_part_* > "$TAR_DIR/$tar_file"; then
        echo "[INFO] Reassembled '${TAR_DIR}/${tar_file}' successfully."
    else
        error_exit "Failed to reassemble '${TAR_DIR}/${tar_file}'."
    fi
done

echo "[INFO] All tar files have been reassembled successfully."
