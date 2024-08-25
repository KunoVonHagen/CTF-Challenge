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

# Check if the GRUB configuration contains systemd.unified_cgroup_hierarchy=0
if grep -q "systemd.unified_cgroup_hierarchy=0" /etc/default/grub; then
    # Remove systemd.unified_cgroup_hierarchy=0 from GRUB_CMDLINE_LINUX
    echo "[INFO] Removing systemd.unified_cgroup_hierarchy=0 from GRUB_CMDLINE_LINUX."
    sed -i 's/ systemd.unified_cgroup_hierarchy=0//' /etc/default/grub
    if [ $? -eq 0 ]; then
        echo "[INFO] Successfully removed the cgroup configuration from GRUB."
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

    # Inform the user to reboot the system
    echo "[INFO] Please reboot your system to apply the changes."
else
    echo "[INFO] systemd.unified_cgroup_hierarchy=0 is not set in GRUB configuration. No changes needed."
fi
