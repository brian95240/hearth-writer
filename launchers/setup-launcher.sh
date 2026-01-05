#!/bin/bash
# Hearth Writer - Universal Launcher Setup
# This script creates a desktop shortcut for any platform

set -e

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear
echo ""
echo -e "${YELLOW}  ╔════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}  ║     🔥 HEARTH WRITER LAUNCHER SETUP    ║${NC}"
echo -e "${YELLOW}  ╚════════════════════════════════════════╝${NC}"
echo ""

# Detect platform
detect_platform() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check if running in WSL
        if grep -qi microsoft /proc/version 2>/dev/null; then
            PLATFORM="wsl"
        else
            PLATFORM="linux"
        fi
    else
        PLATFORM="unknown"
    fi
}

detect_platform
echo -e "${BLUE}Detected platform: ${PLATFORM}${NC}"
echo ""

# Get license key
echo -e "${YELLOW}Step 1: License Key${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$HEARTH_LICENSE_KEY" ]; then
    echo -e "Found existing key: ${GREEN}$HEARTH_LICENSE_KEY${NC}"
    read -p "Use this key? (Y/n): " USE_EXISTING
    if [[ "$USE_EXISTING" =~ ^[Nn] ]]; then
        read -p "Enter your license key: " LICENSE_KEY
    else
        LICENSE_KEY="$HEARTH_LICENSE_KEY"
    fi
else
    read -p "Enter your license key (HRTH_xxx): " LICENSE_KEY
fi

# Validate key format
if [[ ! "$LICENSE_KEY" =~ ^HRTH_(ARCHITECT|SHOWRUNNER)_ ]]; then
    echo -e "${RED}Warning: Key doesn't match expected format (HRTH_ARCHITECT_xxx or HRTH_SHOWRUNNER_xxx)${NC}"
    read -p "Continue anyway? (y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy] ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

echo ""
echo -e "${YELLOW}Step 2: Persistence Option${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "How should we remember your license key?"
echo ""
echo "  1) 🔒 Remember Forever (Recommended)"
echo "     Your key is saved so you never enter it again."
echo ""
echo "  2) 🔑 Ask Each Time"
echo "     Enter your key each time you open Hearth Writer."
echo ""
read -p "Choose option (1 or 2): " PERSIST_OPTION

PERSIST_KEY=false
if [[ "$PERSIST_OPTION" == "1" ]]; then
    PERSIST_KEY=true
fi

echo ""
echo -e "${YELLOW}Step 3: Creating Launcher${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HEARTH_DIR="$HOME/hearth-writer"

case $PLATFORM in
    "macos")
        DESKTOP="$HOME/Desktop"
        LAUNCHER="$DESKTOP/Hearth Writer.command"
        
        if [ "$PERSIST_KEY" = true ]; then
            # Add to shell profile
            SHELL_PROFILE="$HOME/.zshrc"
            if ! grep -q "HEARTH_LICENSE_KEY" "$SHELL_PROFILE" 2>/dev/null; then
                echo "export HEARTH_LICENSE_KEY=\"$LICENSE_KEY\"" >> "$SHELL_PROFILE"
                echo -e "${GREEN}✓ Key saved to $SHELL_PROFILE${NC}"
            fi
            
            cat > "$LAUNCHER" << EOF
#!/bin/bash
# Hearth Writer Launcher
source ~/.zshrc 2>/dev/null
cd ~/hearth-writer
./start.sh
EOF
        else
            cat > "$LAUNCHER" << EOF
#!/bin/bash
# Hearth Writer Launcher
echo "Enter your Hearth Writer license key:"
read -p "Key: " HEARTH_LICENSE_KEY
export HEARTH_LICENSE_KEY
cd ~/hearth-writer
./start.sh
EOF
        fi
        
        chmod +x "$LAUNCHER"
        echo -e "${GREEN}✓ Created: $LAUNCHER${NC}"
        ;;
        
    "linux")
        DESKTOP="$HOME/Desktop"
        mkdir -p "$DESKTOP"
        LAUNCHER="$DESKTOP/HearthWriter.desktop"
        
        if [ "$PERSIST_KEY" = true ]; then
            # Add to shell profile
            SHELL_PROFILE="$HOME/.bashrc"
            if ! grep -q "HEARTH_LICENSE_KEY" "$SHELL_PROFILE" 2>/dev/null; then
                echo "export HEARTH_LICENSE_KEY=\"$LICENSE_KEY\"" >> "$SHELL_PROFILE"
                echo -e "${GREEN}✓ Key saved to $SHELL_PROFILE${NC}"
            fi
            
            cat > "$LAUNCHER" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Hearth Writer
Comment=Local-first authorship engine
Exec=bash -c "source ~/.bashrc && cd ~/hearth-writer && ./start.sh"
Terminal=true
Categories=Office;TextEditor;
EOF
        else
            cat > "$LAUNCHER" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Hearth Writer
Comment=Local-first authorship engine
Exec=bash -c "echo 'Enter license key:' && read HEARTH_LICENSE_KEY && export HEARTH_LICENSE_KEY && cd ~/hearth-writer && ./start.sh"
Terminal=true
Categories=Office;TextEditor;
EOF
        fi
        
        chmod +x "$LAUNCHER"
        
        # Add to applications menu
        mkdir -p ~/.local/share/applications
        cp "$LAUNCHER" ~/.local/share/applications/
        
        echo -e "${GREEN}✓ Created: $LAUNCHER${NC}"
        echo -e "${GREEN}✓ Added to applications menu${NC}"
        ;;
        
    "wsl")
        # For WSL, create a Windows batch file
        WIN_DESKTOP=$(wslpath "$(wslvar USERPROFILE)/Desktop")
        LAUNCHER="$WIN_DESKTOP/Hearth Writer.bat"
        
        if [ "$PERSIST_KEY" = true ]; then
            # Add to WSL shell profile
            SHELL_PROFILE="$HOME/.bashrc"
            if ! grep -q "HEARTH_LICENSE_KEY" "$SHELL_PROFILE" 2>/dev/null; then
                echo "export HEARTH_LICENSE_KEY=\"$LICENSE_KEY\"" >> "$SHELL_PROFILE"
                echo -e "${GREEN}✓ Key saved to $SHELL_PROFILE${NC}"
            fi
            
            cat > "$LAUNCHER" << EOF
@echo off
title Hearth Writer
echo Starting Hearth Writer...
wsl -e bash -c "source ~/.bashrc && cd ~/hearth-writer && ./start.sh"
EOF
        else
            cat > "$LAUNCHER" << EOF
@echo off
title Hearth Writer
set /p HEARTH_KEY="Enter your license key: "
wsl -e bash -c "export HEARTH_LICENSE_KEY='%HEARTH_KEY%' && cd ~/hearth-writer && ./start.sh"
EOF
        fi
        
        echo -e "${GREEN}✓ Created: $LAUNCHER${NC}"
        ;;
        
    *)
        echo -e "${RED}Unknown platform. Creating generic launcher...${NC}"
        LAUNCHER="$HOME/hearth-writer-launcher.sh"
        
        cat > "$LAUNCHER" << EOF
#!/bin/bash
export HEARTH_LICENSE_KEY="$LICENSE_KEY"
cd ~/hearth-writer
./start.sh
EOF
        chmod +x "$LAUNCHER"
        echo -e "${GREEN}✓ Created: $LAUNCHER${NC}"
        ;;
esac

echo ""
echo -e "${GREEN}  ╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}  ║         ✓ SETUP COMPLETE!              ║${NC}"
echo -e "${GREEN}  ╚════════════════════════════════════════╝${NC}"
echo ""
echo "You can now:"
echo "  • Double-click 'Hearth Writer' on your desktop"
echo "  • Your browser will open to http://localhost:5000"
echo ""
echo -e "${YELLOW}Happy writing! 🔥${NC}"
echo ""
