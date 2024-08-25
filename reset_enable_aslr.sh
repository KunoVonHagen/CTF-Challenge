#!/bin/bash

# Function to display an error message and exit
function error_exit {
    echo "[ERROR] $1"
    exit 1
}

# Check if the script is running as root
if [ "$EUID" -ne 0 ]; then
    error_exit "This script must be run as root."
else
    echo "[INFO] Running as root."
fi

# Reset randomize_va_space to 2 using tee
echo 2 | tee /proc/sys/kernel/randomize_va_space > /tmp/command_output.log 2>&1
if [ $? -eq 0 ]; then
    echo "[INFO] randomize_va_space is reset to 2 (ASLR enabled)."
    rm -f /tmp/command_output.log
else
    error_exit "Failed to reset randomize_va_space to 2."
fi
