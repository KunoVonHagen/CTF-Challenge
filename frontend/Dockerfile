# Use the Ubuntu 20.04 LTS (Focal Fossa) image as the base image
FROM ubuntu:focal

ARG FRONTEND_FLAG_SECRET

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set the timezone to Europe/Berlin
ENV TZ=Europe/Berlin

# Configure the timezone data to use Europe/Berlin
RUN echo "tzdata tzdata/Areas select Europe" | debconf-set-selections
RUN echo "tzdata tzdata/Zones/Europe select Berlin" | debconf-set-selections
# Update the package list from the repositories
RUN apt-get update

# Install basic text editors and utilities
RUN apt-get install -y \
    nano \
    vim \
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

# Install PHP and related CLI tools
RUN apt-get install -y \
    php \
    php-cli

# Install OpenSSH client for SSH access
RUN apt-get install -y openssh-client

# Clean up apt cache and remove temporary files to reduce image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Generate a new SSH key pair for the root user with a 4096-bit RSA key
RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N ""

# Create an empty known_hosts file to store SSH host keys
RUN touch /root/.ssh/known_hosts

# Set the appropriate permissions for the SSH directory and files
RUN chmod 700 /root/.ssh
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 644 /root/.ssh/id_rsa.pub

# Set the working directory to /root
WORKDIR /root

# Copy the contents of the current directory on the host to the /root directory in the container
COPY . /root/

# Install Python dependencies specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

RUN echo $FRONTEND_FLAG_SECRET > /root/secret.txt

RUN gcc -o /root/get_flag /root/get_flag.c -lssl -lcrypto
RUN chmod 550 /root/get_flag
RUN rm /root/get_flag.c

# Expose port 8080 for external access to the container
EXPOSE 8080

# Define the default command to run when the container starts
CMD ["python3", "main.py"]
#CMD ["tail", "-f", "/dev/null"]
