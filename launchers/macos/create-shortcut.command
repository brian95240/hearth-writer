#!/bin/bash
# Hearth Writer Desktop Shortcut Creator for macOS
# Double-click this file to create a desktop launcher

clear
echo ""
echo "  ========================================"
echo "   Hearth Writer - Desktop Shortcut Setup"
echo "  ========================================"
echo ""

read -p "Enter your license key (HRTH_xxx): " LICENSE_KEY

echo ""
echo "Creating desktop shortcut..."

cat > ~/Desktop/HearthWriter.command << EOF
#!/bin/bash
# Hearth Writer Launcher
export HEARTH_LICENSE_KEY="$LICENSE_KEY"
cd ~/hearth-writer
./start.sh
EOF

chmod +x ~/Desktop/HearthWriter.command

echo ""
echo "  ========================================"
echo "   SUCCESS! Shortcut created on Desktop"
echo "  ========================================"
echo ""
echo "Double-click 'HearthWriter' on your desktop to start writing!"
echo ""
read -p "Press Enter to close..."
