#!/bin/bash

python3 main.py &
sudo /usr/local/sbin/sshd -D
