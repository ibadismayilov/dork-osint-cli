#!/bin/bash

# 1. Define paths
INSTALL_DIR="$(pwd)"
RUN_SCRIPT="$INSTALL_DIR/run.sh"

# 2. Grant execution permissions
echo "Setting permissions..."
chmod +x "$INSTALL_DIR/run.sh"
chmod +x "$INSTALL_DIR/setup.sh"

# 3. Create a global symbolic link in /usr/local/bin
# This allows the 'search' command to be used from any directory
echo "Creating global 'search' command..."
sudo ln -sf "$RUN_SCRIPT" /usr/local/bin/search

# 4. Trigger initial setup via run.sh
# This will automatically create the venv and install requirements.txt
echo "-------------------------------------------------------"
echo "Running initial environment setup..."
echo "This may take a moment (Installing dependencies)..."
echo "-------------------------------------------------------"

# We run it with --help to trigger the venv/pip logic in run.sh
./run.sh --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Success: Virtual environment and dependencies are ready!"
else
    echo "⚠️  Note: If you encounter errors, try running 'search' manually to see logs."
fi

echo "-------------------------------------------------------"
echo "🚀 SETUP COMPLETE!"
echo "You can now use the tool by typing: search 'your query'"
echo "Example: search 'admin panel' --filetype php"
echo "-------------------------------------------------------"