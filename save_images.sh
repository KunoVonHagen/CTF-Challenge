#!/bin/bash

# Function to log informational messages
log_info() {
    echo "[INFO] $1"
}

# Function to log error messages and exit
log_error() {
    echo "[ERROR] $1"
    cat /tmp/command_output.log
    exit 1
}

# Ensure the images directory exists
log_info "Ensuring the images directory exists..."
mkdir -p images

# Save the Docker image inside the container
log_info "Saving 'monitoring' Docker image inside the monitoring-host container..."
docker exec monitoring-host sh -c "docker save monitoring -o /root/monitoring.img.tar.new" > /tmp/command_output.log 2>&1
if [ $? -ne 0 ]; then
    log_error "Error executing docker save in container."
else
    log_info "Docker image 'monitoring' saved inside the container successfully."
fi

# Copy the tarball from the container to the host
log_info "Copying 'monitoring' Docker image tarball from the container to the host..."
docker cp monitoring-host:/root/monitoring.img.tar.new images/monitoring.img.tar > /tmp/command_output.log 2>&1
if [ $? -ne 0 ]; then
    log_error "Error copying file from container."
else
    log_info "Docker image 'monitoring' copied to host successfully."
fi

# Save the frontend Docker image directly on the host
log_info "Saving 'frontend' Docker image on the host..."
docker save frontend -o images/frontend.img.tar > /tmp/command_output.log 2>&1
if [ $? -ne 0 ]; then
    log_error "Error saving 'frontend' image."
else
    log_info "Docker image 'frontend' saved successfully."
fi

# Save the backend Docker image directly on the host
log_info "Saving 'backend' Docker image on the host..."
docker save backend -o images/backend.img.tar > /tmp/command_output.log 2>&1
if [ $? -ne 0 ]; then
    log_error "Error saving 'backend' image."
else
    log_info "Docker image 'backend' saved successfully."
fi

# Save the monitoring-host Docker image directly on the host
log_info "Saving 'monitoring-host' Docker image on the host..."
docker save monitoring-host -o images/monitoring-host.img.tar > /tmp/command_output.log 2>&1
if [ $? -ne 0 ]; then
    log_error "Error saving 'monitoring-host' image."
else
    log_info "Docker image 'monitoring-host' saved successfully."
fi

log_info "All images saved successfully."
