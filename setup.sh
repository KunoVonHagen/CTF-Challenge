#!/bin/bash

# Function to display an error message and exit
function error_exit {
    echo "[ERROR] $1"
    cat /tmp/command_output.log
    exit 1
}

# Function to monitor the Docker container logs
function monitor_container_logs {
    local container_name=$1
    local success_message='\[+\] Monitoring container is running'
    local test='\[+\] Waiting for Docker daemon to start...'
    local log_file=/tmp/container_logs.log

    while true; do
        docker logs $container_name > $log_file 2>&1

        if grep -q '\[-\]' $log_file; then
            echo "[ERROR] Error detected in container logs."
            cat $log_file
            exit 1
        elif grep -q "$success_message" $log_file; then
            echo "[INFO] Success message detected. The monitoring service has been set up."
            rm -f $log_file
            break
        fi
        sleep 1
    done
}

# Check if the script is running as root
if [ "$EUID" -ne 0 ]; then
    error_exit "This script must be run as root."
else
    echo "[INFO] Running as root."
fi

# Check if cgroup is v1 by inspecting /sys/fs/cgroup for typical cgroup v1 directories
if [ -d "/sys/fs/cgroup" ]; then
    if [ -d "/sys/fs/cgroup/cpu" ] || [ -d "/sys/fs/cgroup/memory" ] || [ -d "/sys/fs/cgroup/blkio" ]; then
        echo "[INFO] cgroup v1 is in use."
    elif [ -e "/sys/fs/cgroup/cgroup.controllers" ]; then
        error_exit "This system is using cgroup v2. Please switch to cgroup v1 to run this challenge."
    else
        error_exit "Unable to determine cgroup version. Please ensure that cgroup v1 is in use."
    fi
else
    error_exit "/sys/fs/cgroup directory does not exist. Cannot determine cgroup version."
fi

# Set randomize_va_space to 0 using tee
echo 0 | tee /proc/sys/kernel/randomize_va_space > /tmp/command_output.log 2>&1
if [ $? -eq 0 ]; then
    echo "[INFO] randomize_va_space is set to 0 (ASLR disabled)."
    rm -f /tmp/command_output.log
else
    error_exit "Failed to set randomize_va_space to 0."
fi

# Take down any existing Docker containers
echo "[INFO] Stopping and removing any existing Docker containers..."
docker compose down > /tmp/command_output.log 2>&1
if [ $? -eq 0 ]; then
    echo "[INFO] Docker containers stopped and removed successfully."
    rm -f /tmp/command_output.log
else
    error_exit "Failed to stop and remove Docker containers."
fi

# Build Docker images
echo "[INFO] Building Docker images..."
docker compose build > /tmp/command_output.log 2>&1
if [ $? -eq 0 ]; then
    echo "[INFO] Docker images built successfully."
    rm -f /tmp/command_output.log
else
    error_exit "Failed to build Docker images."
fi

# Start Docker Compose
echo "[INFO] Starting Docker containers using Docker Compose..."
docker compose up -d > /tmp/command_output.log 2>&1
if [ $? -eq 0 ]; then
    echo "[INFO] Docker containers started successfully."
    rm -f /tmp/command_output.log
else
    error_exit "Failed to start Docker containers."
fi

echo "[INFO] Waiting for the monitoring service to start up..."

# Monitor logs of the monitoring container
monitor_container_logs "monitoring-host"

echo "[INFO] Challenge environment is ready."
echo "[INFO] To access the challenge more easily add '<host ip> ctf-challenge.edu' to your attacking systems /etc/hosts file"
