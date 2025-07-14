#!/bin/bash

# Please replace apt-get with yum if you are using Amazon AMI, which uses RHEL
sudo apt-get update
sudo apt-get install python3.12 -y
# Install other packages
sudo apt-get install pip -y
sudo apt-get install zip -y
# Install and activate Python venv
sudo apt install python3.12-venv
python3 -m venv python_env
source python_env/bin/activate
# Install Python packages
pip install -r requirements.txt
