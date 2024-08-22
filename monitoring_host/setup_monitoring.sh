#!/bin/ash
echo "Waiting for Docker daemon to start..."
while [ ! -e /var/run/docker.sock ]; do
    sleep 1
done
echo "Docker daemon started, initiating building monitoring container"

# Build the attacker container image
echo "Starting to build the monitoring image"
docker build --build-arg MONITORING_FLAG1_SECRET=$MONITORING_FLAG1_SECRET --build-arg MONITORING_FLAG2_SECRET=$MONITORING_FLAG2_SECRET -f MonitoringDockerfile -t monitoring . 
echo "Finished building the monitoring image"

# Run the attacker container where CVE-2019-5736 can be exploited
echo "Starting the monitoring container"
docker run -e MONITORING_INTERVAL_SECONDS=$MONITORING_INTERVAL_SECONDS -e MONITORING_SESSION_SECRET=$MONITORING_SESSION_SECRET --network="host" --dns 8.8.8.8 --dns 8.8.4.4 --mount type=bind,source=/etc/hosts,target=/etc/hosts,readonly --name monitoring -dit monitoring
echo "Monitoring container is running"

while true; do
	echo "just executed" > /root/last_execution.txt
	date >> /root/last_execution.txt
    docker exec -u root -dit monitoring /root/check_monitoring.sh >> /root/last_execution.txt 2>> /root/last_execution.txt
	
	sleep $MONITORING_HOST_CHECK_MONITORING_INTERVAL_SECONDS
done
