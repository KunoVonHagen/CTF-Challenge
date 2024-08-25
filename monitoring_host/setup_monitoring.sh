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

# Build the attacker container image
log_message "[+]" "Starting to build the monitoring image"
if docker build --build-arg MONITORING_FLAG1_SECRET=$MONITORING_FLAG1_SECRET --build-arg MONITORING_FLAG2_SECRET=$MONITORING_FLAG2_SECRET -f MonitoringDockerfile -t monitoring .; then
    log_message "[+]" "Finished building the monitoring image"
else
    log_message "[-]" "Failed to build the monitoring image"
    exit 1
fi

# Run the attacker container where CVE-2019-5736 can be exploited
log_message "[+]" "Starting the monitoring container"
if docker run -e MONITORING_INTERVAL_SECONDS=$MONITORING_INTERVAL_SECONDS -e MONITORING_SESSION_SECRET=$MONITORING_SESSION_SECRET --network="host" --dns 8.8.8.8 --dns 8.8.4.4 --mount type=bind,source=/etc/hosts,target=/etc/hosts,readonly --name monitoring -dit monitoring; then
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
