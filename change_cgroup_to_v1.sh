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

# Define the parameters to be added
PARAM1="systemd.unified_cgroup_hierarchy=0"
PARAM2="SYSTEMD_CGROUP_ENABLE_LEGACY_FORCE=1"

# Function to add a parameter to GRUB_CMDLINE_LINUX if not already present
function add_grub_param {
    local param="$1"
    if grep -q "$param" /etc/default/grub; then
        echo "[INFO] $param is already set in GRUB configuration."
    else
        echo "[INFO] Adding $param to GRUB_CMDLINE_LINUX."
        sed -i "s/GRUB_CMDLINE_LINUX=\"\(.*\)\"/GRUB_CMDLINE_LINUX=\"\1 $param\"/" /etc/default/grub
        if [ $? -eq 0 ]; then
            echo "[INFO] Successfully added $param to GRUB."
        else
            error_exit "Failed to modify the GRUB configuration for $param."
        fi
    fi
}

# Add both parameters to GRUB_CMDLINE_LINUX
add_grub_param "$PARAM1"
add_grub_param "$PARAM2"

# Update GRUB
echo "[INFO] Updating GRUB configuration..."
update-grub
if [ $? -eq 0 ]; then
    echo "[INFO] GRUB configuration updated successfully."
else
    error_exit "Failed to update GRUB."
fi

# Inform the user to reboot the system
echo "[INFO] Please reboot your system to apply the changes."
