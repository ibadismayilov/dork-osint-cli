#!/bin/bash

# 1. Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed on this system."
    exit 1
fi

# 2. Setup/Activate virtual environment
if [ ! -d "venv" ]; then
    echo "-------------------------------------------------------"
    echo "Initial Setup: Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "Warning: requirements.txt not found!"
    fi
    echo "Setup complete!"
    echo "-------------------------------------------------------"
else
    # Just activate if venv already exists
    source venv/bin/activate
fi

# 3. Execute the main program
# Passing all arguments ($@) to main.py
python3 main.py "$@"