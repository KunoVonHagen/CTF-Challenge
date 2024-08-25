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

# Check if the GRUB configuration already contains the setting
if grep -q "systemd.unified_cgroup_hierarchy=0" /etc/default/grub; then
    echo "[INFO] systemd.unified_cgroup_hierarchy=0 is already set in GRUB configuration."
else
    # Add systemd.unified_cgroup_hierarchy=0 to GRUB_CMDLINE_LINUX
    echo "[INFO] Adding systemd.unified_cgroup_hierarchy=0 to GRUB_CMDLINE_LINUX."
    sed -i 's/GRUB_CMDLINE_LINUX="\(.*\)"/GRUB_CMDLINE_LINUX="\1 systemd.unified_cgroup_hierarchy=0"/' /etc/default/grub
    if [ $? -eq 0 ]; then
        echo "[INFO] Successfully added the cgroup configuration to GRUB."
    else
        error_exit "Failed to modify the GRUB configuration."
    fi

    # Update GRUB
    echo "[INFO] Updating GRUB configuration..."
    update-grub
    if [ $? -eq 0 ]; then
        echo "[INFO] GRUB configuration updated successfully."
    else
        error_exit "Failed to update GRUB."
    fi
fi

# Inform the user to reboot the system
echo "[INFO] Please reboot your system to apply the changes."
