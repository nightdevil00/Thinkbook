#!/bin/bash

# --- VARIABLES ---
SOURCE_DIR="./Fonts"
DEST_DIR="/usr/local/share/fonts"

# --- MAIN SCRIPT ---

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: The '$SOURCE_DIR' directory does not exist."
    exit 1
fi

echo "Copying fonts from '$SOURCE_DIR' to '$DEST_DIR'..."

# Copy the font files
sudo cp -r "$SOURCE_DIR"/* "$DEST_DIR"

# Update the font cache
echo "Updating font cache..."
sudo fc-cache -f -v

echo "Done! The fonts have been installed."
