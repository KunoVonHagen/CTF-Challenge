#!/bin/bash

touch images/monitoring.img.tar

# Function to display an error message and exit
function error_exit {
    echo "[ERROR] $1"
    cat /tmp/command_output.log
    exit 1
}

display_help() {
    echo "Usage: $(basename $0) [options]"
    echo
    echo "Options:"
    echo "  -b    Build images."
    echo "  -l    Load images."
    echo "  -h    Display this help message."
    echo
    echo "If no options are provided, this help message will be displayed."
    echo "You cannot use both -b (build images) and -l (load images) together."
    exit 0
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

# Function to build Docker images
function build_images {
    echo "[INFO] Building Docker images..."
    docker compose build > /tmp/command_output.log 2>&1
    if [ $? -eq 0 ]; then
        echo "[INFO] Docker images built successfully."
        rm -f /tmp/command_output.log
    else
        error_exit "Failed to build Docker images."
    fi
}

# Function to assemble tar files if they don't exist
function assemble_tar_files {
    # Define the directory and filenames
    local directory="images"
    local files=("monitoring.img.tar" "backend.img.tar" "monitoring-host.img.tar" "frontend.img.tar")

    # Flag to track if any file is missing
    local all_files_exist=true

    # Check if each file exists
    echo "[INFO] Checking if tar files are present in the '$directory' directory..."

    for file in "${files[@]}"; do
        if [ ! -f "${directory}/${file}" ]; then
            all_files_exist=false
            echo "[WARNING] Missing tar file: ${directory}/${file}"
        fi
    done

    # Execute the script if any file is missing
    if [ "$all_files_exist" = false ]; then
        echo "[INFO] One or more tar files are missing. Assembling tar files..."
        bash assemble_tars.sh
        if [ $? -eq 0 ]; then
            echo "[INFO] Tar files assembled successfully."
            rm -f /tmp/assemble_tars_output.log
        else
            error_exit "Failed to assemble tar files. Check /tmp/assemble_tars_output.log for details."
        fi
    else
        echo "[INFO] All tar files are present. No need to assemble."
    fi
}

# Function to load Docker images from tarballs
function load_images {
    local images_dir="images"
    local images=("monitoring-host" "frontend" "backend")

    echo "[INFO] Loading Docker images from tarballs..."

    assemble_tar_files

    for image in "${images[@]}"; do
    	echo "[INFO] Loading Docker image '$image'..."
    
        docker import $images_dir/$image.img.tar > /tmp/command_output.log 2>&1
        if [ $? -eq 0 ]; then
            echo "[INFO] Docker image '$image' loaded successfully."
        else
            error_exit "Failed to load Docker image '$image'."
        fi
    done

    rm -f /tmp/command_output.log
}

# Function to check if required commands are available
function check_docker_installation {
    echo "[INFO] Checking if 'docker' and 'docker compose' are valid commands..." 
    
    docker version > /dev/null 2> /dev/null
    
    if ! [ $? -eq 0 ]; then
        error_exit "Couldn't find 'docker'. Please install docker-ce and docker-ce-cli"
    fi
    
    docker compose version > /dev/null 2> /dev/null    

    if ! [ $? -eq 0 ]; then
        error_exit "Couldn't find 'docker compose'. Please install the Compose plugin for docker"
    fi
    
    echo "[INFO] 'docker' and 'docker compose' are valid commands. Continuing" 
}

# Default values for options
build_images_flag=false
load_images_flag=false

# Parse options
while getopts ":blh" opt; do
    case $opt in
        b)
            build_images_flag=true
            ;;
        l)
            load_images_flag=true
            ;;
        h)
            display_help
            ;;
        \?)
            echo "[ERROR] Invalid option: -$OPTARG"
            display_help
            ;;
    esac
done

# If no options were passed, display help and exit
if [ $OPTIND -eq 1 ]; then
    display_help
fi

# Ensure that only one of -b or -i is specified
if [ "$build_images_flag" = true ] && [ "$load_images_flag" = true ]; then
    error_exit "Cannot use both -b and -i options together."
elif [ "$build_images_flag" = false ] && [ "$load_images_flag" = false ]; then
    display_help
fi

# Check if the script is running as root
if [ "$EUID" -ne 0 ]; then
    error_exit "This script must be run as root."
else
    echo "[INFO] Running as root."
fi

# Check if Docker and Docker Compose are installed
check_docker_installation

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

# Execute the selected action
if [ "$build_images_flag" = true ]; then
    build_images
    export LOAD_IMAGES=false
elif [ "$load_images_flag" = true ]; then
    load_images
    export LOAD_IMAGES=true
fi

# Take down any existing Docker containers
echo "[INFO] Stopping and removing existing Docker containers..."
docker compose down > /tmp/command_output.log 2>&1

# Check the exit status of the docker-compose command
if [ $? -eq 0 ]; then
    echo "[INFO] Docker containers stopped and removed successfully."
else
    error_exit "Failed to stop and remove Docker containers."
    exit 1
fi

# Start Docker containers
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
echo "[INFO] To access the challenge more easily, add '<host ip> ctf-challenge.edu' to your attacking system's /etc/hosts file."
