# CTF Challenge Setup Guide

## Introduction

This guide will walk you through the steps required to set up a Capture The Flag (CTF) challenge environment on a virtual machine (VM). The setup involves disabling ASLR (Address Space Layout Randomization), configuring the system to use cgroup v1, and running Docker containers. After completing the challenge, scripts are provided to reset these settings to their original state. **It is highly recommended to run this setup in a VM**, as it involves changes that may reduce the security of your host system.

## Prerequisites

1. **Virtual Machine (VM):** Ensure that you are running these scripts on a VM to avoid compromising your main system.
2. **Root Privileges:** You must have root access to execute the scripts.
3. **Docker:** You must have docker-ce and docker-ce-cli as well as the Compose plugin installed.

## Files Overview

1. **`setup.sh`:** This script sets up the CTF challenge environment.
2. **`change_cgroup_to_v1.sh`:** This script configures the system to use cgroup v1, which is necessary for the challenge.
3. **`reset_cgroup_to_v2.sh`:** This script resets the system to use cgroup v2 after the challenge is completed.
4. **`reset_enable_aslr.sh`:** This script re-enables ASLR after the challenge is completed.

## Setup Instructions

### 1. Prepare the VM
- Ensure that you have a Linux-based VM ready.
- You must have root access to the VM, as these scripts require elevated privileges.

### 2. Set Cgroup to v1

Run the `change_cgroup_to_v1.sh` script to configure your system to use cgroup v1:

```bash
sudo bash change_cgroup_to_v1.sh
```

- This script checks if cgroup v1 is already enabled. If not, it adds the required configuration to the GRUB bootloader and updates GRUB.
- **Important:** After running this script, you will need to reboot the VM to apply the changes.

### 3. Disable ASLR

Run the `setup.sh` script, which includes steps to disable ASLR:

```bash
sudo bash setup.sh -l
```

- The `-l` flag makes the script load the built images from the `images` directory. The `-b` flag can be used to build them from source
- This script disables ASLR by setting `randomize_va_space` to `0`.
- The script also stops any running Docker containers, builds the required Docker images, and starts the Docker containers necessary for the challenge.
- Ensure that ASLR is disabled for the challenge to function as intended.

### 4. Start the CTF Challenge

After completing the setup, the CTF environment will be ready. You can now access the challenge through the Docker containers that have been started.

- The challenge environment is exposed and accessible from outside the VM, so ensure that your VM's network is configured appropriately.

## Post-Challenge Cleanup

Once the challenge is completed, follow these steps to reset the system to its original state:

### 1. Re-enable ASLR

Run the `reset_enable_aslr.sh` script to re-enable ASLR:

```bash
sudo bash reset_enable_aslr.sh
```

- This script sets `randomize_va_space` back to `2`, restoring ASLR.

### 2. Reset Cgroup to v2

Run the `reset_cgroup_to_v2.sh` script to revert the cgroup configuration to v2:

```bash
sudo bash reset_cgroup_to_v2.sh
```

- This script removes the cgroup v1 configuration from the GRUB bootloader and updates GRUB.
- **Important:** After running this script, you will need to reboot the VM to apply the changes.

## Important Notes

- **Security Warning:** Disabling ASLR and switching to cgroup v1 reduces the security of your system. This setup should only be used in a controlled environment, such as a VM designed for testing or CTF challenges.
- **Rebooting:** Some changes require a system reboot to take effect. Ensure you reboot the VM when instructed.
- **Docker Containers:** The Docker containers used for the challenge are vulnerable by design. Do not expose this VM to untrusted networks.

By following these steps, you can safely set up, run, and clean up after a CTF challenge on a VM.
