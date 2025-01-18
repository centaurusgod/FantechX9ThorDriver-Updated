#!/bin/bash

# Add the current user to the 'users' group
sudo usermod -aG users "$USER"

# Set the udev rules for the Fantech X9 Thor gaming mouse
echo 'SUBSYSTEMS=="usb", ATTRS{idVendor}=="18f8", ATTRS{idProduct}=="0fc0", GROUP="users", MODE="0660"' | sudo tee /etc/udev/rules.d/50-fantechdriver.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Make the 'mouse' script executable
chmod +x mouse

# Copy the 'mouse' script to /usr/bin/ with sudo permissions
sudo cp mouse /usr/bin/
