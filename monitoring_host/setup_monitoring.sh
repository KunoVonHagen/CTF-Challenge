#!/bin/ash

# Function to log messages with timestamps and prefixes
log_message() {
    local prefix=$1
    local message=$2
    echo "$prefix $message"
}

# Wait for Docker daemon to start
log_message "[+]" "Waiting for Docker daemon to start..."
while [ ! -e /var/run/docker.sock ]; do
    sleep 1
done
log_message "[+]" "Docker daemon started, initiating building monitoring container"

# Check if the image should be built or loaded
if [ "$LOAD_IMAGES" = false ]; then
    log_message "[+]" "Building the monitoring image"
    if docker build --build-arg MONITORING_FLAG1_SECRET=$MONITORING_FLAG1_SECRET --build-arg MONITORING_FLAG2_SECRET=$MONITORING_FLAG2_SECRET -f MonitoringDockerfile -t monitoring .; then
        log_message "[+]" "Finished building the monitoring image"
    else
        log_message "[-]" "Failed to build the monitoring image"
        exit 1
    fi
else
    log_message "[+]" "Loading the monitoring image from tarball"
    if docker load -i /root/monitoring.img.tar; then
        log_message "[+]" "Finished loading the monitoring image"
    else
        log_message "[-]" "Failed to load the monitoring image"
        exit 1
    fi
fi

# Run the monitoring container where CVE-2019-5736 can be exploited
log_message "[+]" "Starting the monitoring container"
if docker run --network="host" --dns 8.8.8.8 --dns 8.8.4.4 --mount type=bind,source=/etc/hosts,target=/etc/hosts,readonly --name monitoring -dit monitoring; then
    log_message "[+]" "Monitoring container is running"
else
    log_message "[-]" "Failed to start the monitoring container"
    exit 1
fi

while true; do
    echo "just executed" > /root/last_execution.txt
    date >> /root/last_execution.txt
    docker exec -u root -dit monitoring /root/check_monitoring.sh >> /root/last_execution.txt 2>> /root/last_execution.txt
    sleep $MONITORING_HOST_CHECK_MONITORING_INTERVAL_SECONDS
done
