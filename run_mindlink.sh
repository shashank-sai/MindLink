#!/bin/bash

# MindLink Therapy Assistant Launcher
# For Linux and macOS systems

echo "MindLink Therapy Assistant"
echo "=========================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

# Check if required packages are installed
echo "Checking required packages..."
if ! pip3 show ollama &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install required packages"
        echo "Please check your internet connection and try again"
        exit 1
    fi
fi

echo
echo "Starting MindLink Therapy Assistant..."
echo

# Start the application
python3 main.py

echo
echo "MindLink session ended."