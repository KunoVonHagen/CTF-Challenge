#!/bin/bash

# Function to display an error message and exit
function error_exit {
    echo "[ERROR] $1"
    cat /tmp/command_output.log
    exit 1
}

# Function to check if the script is run as root
function check_root {
    if [ "$EUID" -ne 0 ]; then
        error_exit "This script must be run as root."
    else
        echo "[INFO] Running as root."
    fi
}

# Function to stop and remove Docker containers
function stop_and_remove_containers {
    echo "[INFO] Stopping and removing Docker containers..."
    docker compose down > /tmp/command_output.log 2>&1

    if [ $? -eq 0 ]; then
        echo "[INFO] Docker containers stopped and removed successfully."
        rm -f /tmp/command_output.log
    else
        error_exit "Failed to stop and remove Docker containers."
    fi
}

# Check if the script is running as root
check_root

# Stop and remove Docker containers
stop_and_remove_containers

echo "[INFO] CTF environment has been shut down and cleaned up. Goodbye!"
