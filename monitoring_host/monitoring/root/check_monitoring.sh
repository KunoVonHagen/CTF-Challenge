#!/bin/bash

# Define the program and user
program_name="main.py"
user_name="monitoring"
script_path="/home/monitoring/main.py"

# Check if the program is running
if ! pgrep -u "$user_name" -f "$script_path" > /dev/null
then
    # Start the program as the specified user
    sudo -u "$user_name" python3 "$script_path" &
fi

echo "just checked the monitoring" > /home/monitoring/last_execution.txt
date >> /home/monitoring/last_execution.txt
