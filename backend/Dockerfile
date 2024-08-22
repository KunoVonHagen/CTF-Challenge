# Use the Ubuntu 20.04 LTS (Focal Fossa) image as the base image
FROM ubuntu:focal

ARG BACKEND_FLAG1_SECRET
ARG BACKEND_FLAG2_SECRET
ARG BACKEND_ADMIN_USER
ARG BACKEND_ADMIN_PASSWORD

ENV BACKEND_ADMIN_USER=$BACKEND_ADMIN_USER

# Set the frontend to noninteractive to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install necessary packages
RUN apt-get update

# Update the package list to get the latest information about available packages
RUN apt-get update

# Install basic text editors and utilities
RUN apt-get install -y \
    nano \
    less \
    coreutils \
    curl \
    wget \
    netcat \
    git \
    net-tools

# Install essential build tools and utilities
RUN apt-get install -y \
    gcc \
    libssl-dev \
    make \
    cmake \
    build-essential \
    tar \
    unzip

# Install Python 3 and related tools
RUN apt-get install -y \
    python3 \
    python3-pip \
    python3-venv

# Install development libraries required for various software compilations
RUN apt-get install -y \
    zlib1g-dev \
    libssl-dev \
    libpam0g-dev \
    libselinux1-dev \
    libkrb5-dev \
    libedit-dev \
    libwrap0-dev

# Clean up apt cache and remove temporary files to reduce image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download OpenSSL 1.0.2u
RUN wget https://www.openssl.org/source/openssl-1.0.2u.tar.gz

# Extract and configure OpenSSL
RUN tar -xzf openssl-1.0.2u.tar.gz
RUN cd openssl-1.0.2u && ./config

# Build and install OpenSSL
RUN cd openssl-1.0.2u && make
RUN cd openssl-1.0.2u && make install

# Replace the default OpenSSL binary with the newly built version
RUN rm -f /usr/bin/openssl
RUN ln -s /usr/local/ssl/bin/openssl /usr/bin/openssl

# Download OpenSSH 7.7p1
RUN wget http://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-7.7p1.tar.gz

# Extract and configure OpenSSH with OpenSSL support
RUN tar -xzf openssh-7.7p1.tar.gz
RUN cd openssh-7.7p1 && ./configure --with-ssl-dir=/usr/local/ssl

# Build and install OpenSSH
RUN cd openssh-7.7p1 && make
RUN cd openssh-7.7p1 && make install

# Clean up the downloaded tar files and directories
RUN rm -rf openssl-1.0.2u.tar.gz openssl-1.0.2u
RUN rm -rf openssh-7.7p1.tar.gz openssh-7.7p1

# Create a system user and group for SSH daemon
RUN groupadd -r sshd && useradd -r -g sshd -s /sbin/nologin -d /var/empty sshd
RUN mkdir -p /var/run/sshd

# Configure SSH server to allow password authentication and other basic settings
RUN sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /usr/local/etc/sshd_config
RUN sed -i 's/^#PermitRootLogin prohibit-password/PermitRootLogin no/' /usr/local/etc/sshd_config
RUN sed -i 's/^#PermitEmptyPasswords no/PermitEmptyPasswords no/' /usr/local/etc/sshd_config

# Install a specific vulnerable version of sudo
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/s/sudo/sudo_1.8.21p2-3ubuntu1_amd64.deb
RUN dpkg -i sudo_1.8.21p2-3ubuntu1_amd64.deb
RUN apt-get install -f
RUN rm sudo_1.8.21p2-3ubuntu1_amd64.deb

# Create a new user 
RUN useradd -m $BACKEND_ADMIN_USER

# Set a password for the user
RUN echo $BACKEND_ADMIN_USER":"$BACKEND_ADMIN_PASSWORD | chpasswd

# Configure sudoers to demonstrate vulnerability
RUN echo $BACKEND_ADMIN_USER" ALL=(ALL, !root) NOPASSWD: ALL" >> /etc/sudoers.d/$BACKEND_ADMIN_USER
RUN echo $BACKEND_ADMIN_USER" ALL=(ALL:ALL) NOPASSWD: /usr/local/sbin/sshd" >> /etc/sudoers.d/$BACKEND_ADMIN_USER

# Set working directory and copy application files
WORKDIR /home/$BACKEND_ADMIN_USER
COPY app /home/$BACKEND_ADMIN_USER/
COPY root /root/

# Set permissions for the /home/$BACKEND_ADMIN_USER directory
RUN chmod -R 777 /home/$BACKEND_ADMIN_USER/
RUN chown -R $BACKEND_ADMIN_USER:$BACKEND_ADMIN_USER /home/$BACKEND_ADMIN_USER/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Make the start script executable
RUN chmod +x /home/$BACKEND_ADMIN_USER/start_backend.sh

RUN echo $BACKEND_FLAG2_SECRET > /root/secret.txt

RUN gcc -o /root/get_flag /root/get_flag.c -lssl -lcrypto
RUN chmod 550 /root/get_flag
RUN rm /root/get_flag.c

# Switch to the $BACKEND_ADMIN_USER user
USER $BACKEND_ADMIN_USER

RUN echo $BACKEND_FLAG1_SECRET > /home/$BACKEND_ADMIN_USER/secret.txt

RUN gcc -o /home/$BACKEND_ADMIN_USER/get_flag /home/$BACKEND_ADMIN_USER/get_flag.c -lssl -lcrypto
RUN chmod 550 /home/$BACKEND_ADMIN_USER/get_flag
RUN rm /home/$BACKEND_ADMIN_USER/get_flag.c

# Set the default command to run the start script
CMD /home/$BACKEND_ADMIN_USER/start_backend.sh
