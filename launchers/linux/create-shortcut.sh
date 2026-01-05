#!/bin/bash
# Hearth Writer Desktop Shortcut Creator for Linux
# Run this script to create a desktop launcher

clear
echo ""
echo "  ========================================"
echo "   Hearth Writer - Desktop Shortcut Setup"
echo "  ========================================"
echo ""

read -p "Enter your license key (HRTH_xxx): " LICENSE_KEY

echo ""
echo "Creating desktop shortcut..."

# Create .desktop file
cat > ~/Desktop/HearthWriter.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Hearth Writer
Comment=Local-first authorship engine
Exec=bash -c "export HEARTH_LICENSE_KEY='$LICENSE_KEY' && cd ~/hearth-writer && ./start.sh"
Icon=$HOME/hearth-writer/frontend/public/logo.png
Terminal=true
Categories=Office;TextEditor;
EOF

chmod +x ~/Desktop/HearthWriter.desktop

# Also create in applications menu
mkdir -p ~/.local/share/applications
cp ~/Desktop/HearthWriter.desktop ~/.local/share/applications/

echo ""
echo "  ========================================"
echo "   SUCCESS! Shortcut created on Desktop"
echo "  ========================================"
echo ""
echo "Double-click 'Hearth Writer' on your desktop to start writing!"
echo "It's also available in your applications menu."
echo ""
read -p "Press Enter to close..."
