#!/bin/bash

# Update package lists
echo "Updating package lists..."
sudo apt update -y

# Install Python 3.11
echo "Installing Python 3.11..."
sudo apt install python3.11 -y

# Install pip for Python 3
echo "Installing pip for Python 3..."
sudo apt install python3-pip -y

# Install dependencies from requirements.txt
echo "Installing Python dependencies..."
python3.11 -m pip install -r requirements.txt

# Install ffmpeg
echo "Installing ffmpeg..."
sudo apt install ffmpeg -y

# Run the Python app with Python 3.11
echo "Running the Python app..."
python3.11 main.py
