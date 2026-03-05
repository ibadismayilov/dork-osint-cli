#!/bin/bash

# Make run.sh executable
chmod +x run.sh

# Detect the shell configuration file (.bashrc or .zshrc)
if [ -n "$($SHELL -c 'echo $ZSH_VERSION')" ]; then
    CONF_FILE="$HOME/.zshrc"
elif [ -n "$($SHELL -c 'echo $BASH_VERSION')" ]; then
    CONF_FILE="$HOME/.bashrc"
else
    echo "Error: Compatible shell not found. Please add the alias manually."
    exit 1
fi

# Get the absolute path of the current directory
CURRENT_DIR=$(pwd)

# Check if the alias already exists
if ! grep -q "alias search=" "$CONF_FILE"; then
    echo "" >> "$CONF_FILE"
    echo "# Terminal Search System Alias" >> "$CONF_FILE"
    echo "alias search='$CURRENT_DIR/run.sh'" >> "$CONF_FILE"
    
    echo "-------------------------------------------------------"
    echo "Success! The 'search' command has been created."
    echo "Please run: source $CONF_FILE"
    echo "Now you can use the tool by typing 'search' anywhere."
    echo "-------------------------------------------------------"
else
    echo "Notice: Alias 'search' already exists in $CONF_FILE."
fi