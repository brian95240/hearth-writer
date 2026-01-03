#!/bin/bash
# Hearth Writer v1.2 "Vertex" - Setup Script
# Usage: curl -sSL https://raw.githubusercontent.com/brian95240/hearth-writer/main/setup.sh | bash
#
# This script performs a full, cascading installation of Hearth Writer.

set -e

# === Configuration ===
ENV_NAME="hearth_env"
PYTHON_VER="3.11"
MODEL_DIR="./models"
CACHE_DIR="./data/cache/audio_lru"
GRAMMAR_DIR="./core/grammars"
DATA_DIR="./data"
LOGS_DIR="./logs"
SYNC_DIR="./sync"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === Banner ===
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   HEARTH WRITER v1.2 \"VERTEX\" - CASCADING INSTALLATION        ║"
echo "║   Collapse-to-Zero Architecture | Privacy Absolute            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# === Parse Arguments ===
MODELS_ONLY=false
SKIP_VENV=false
WITH_MODELS=false

for arg in "$@"; do
    case $arg in
        --models-only)
            MODELS_ONLY=true
            shift
            ;;
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --with-models)
            WITH_MODELS=true
            shift
            ;;
        --help)
            echo "Usage: ./setup.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --models-only   Only download AI models (skip environment setup)"
            echo "  --with-models   Include model download in full installation"
            echo "  --skip-venv     Skip virtual environment creation"
            echo "  --help          Show this help message"
            echo ""
            echo "One-Line Install:"
            echo "  curl -sSL https://raw.githubusercontent.com/brian95240/hearth-writer/main/setup.sh | bash"
            exit 0
            ;;
    esac
done

# === Step 1: Environment Initialization ===
echo -e "${BLUE}>> [1/6] Initializing Hearth Environment ($ENV_NAME)...${NC}"

# Check Python version
if ! command -v python$PYTHON_VER &> /dev/null; then
    # Try python3 as fallback
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        ACTUAL_VER=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$(printf '%s\n' "3.11" "$ACTUAL_VER" | sort -V | head -n1)" != "3.11" ]; then
            echo -e "${RED}Error: Python 3.11+ required. Found: $ACTUAL_VER${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Error: Python $PYTHON_VER is required.${NC}"
        echo "Install with: sudo apt install python3.11 python3.11-venv"
        exit 1
    fi
else
    PYTHON_CMD="python$PYTHON_VER"
fi

echo -e "${GREEN}✓${NC} Python detected: $($PYTHON_CMD --version)"

# Clone repository if not already in it
if [ ! -f "app.py" ]; then
    echo ""
    echo "Cloning Hearth Writer repository..."
    git clone https://github.com/brian95240/hearth-writer.git
    cd hearth-writer
fi

# Create virtual environment
if [ "$SKIP_VENV" = false ] && [ "$MODELS_ONLY" = false ]; then
    if [ -d "$ENV_NAME" ]; then
        echo -e "${YELLOW}!${NC} Virtual environment exists, reusing..."
    else
        $PYTHON_CMD -m venv $ENV_NAME
    fi
    source $ENV_NAME/bin/activate
    pip install --upgrade pip --quiet
    echo -e "${GREEN}✓${NC} Virtual environment ready"
fi

# === Step 2: Install Dependencies ===
if [ "$MODELS_ONLY" = false ]; then
    echo ""
    echo -e "${BLUE}>> [2/6] Installing Dependencies...${NC}"
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓${NC} All dependencies installed"
fi

# === Step 3: Directory Structure ===
echo ""
echo -e "${BLUE}>> [3/6] Creating Directory Structure...${NC}"

mkdir -p "$MODEL_DIR"
mkdir -p "$CACHE_DIR"
mkdir -p "$GRAMMAR_DIR"
mkdir -p "$DATA_DIR/series_db/project"
mkdir -p "$DATA_DIR/users"
mkdir -p "$DATA_DIR/schemas"
mkdir -p "$LOGS_DIR"
mkdir -p "$SYNC_DIR"
mkdir -p "./frontend/public"

# Create .gitkeep files for empty directories
touch "$MODEL_DIR/.gitkeep"
touch "$CACHE_DIR/.gitkeep"
touch "$LOGS_DIR/.gitkeep"

echo -e "${GREEN}✓${NC} Directory structure created"

# === Step 4: Hardware Profiling ===
echo ""
echo -e "${BLUE}>> [4/6] Profiling Hardware...${NC}"

# Detect GPU
GPU_TYPE="cpu"
GPU_LAYERS=0

if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "")
    if [ -n "$GPU_INFO" ]; then
        GPU_TYPE="cuda"
        GPU_MEM=$(echo "$GPU_INFO" | awk -F',' '{print $2}' | tr -d ' MiB')
        # Calculate layers based on VRAM (rough estimate)
        if [ "$GPU_MEM" -gt 8000 ]; then
            GPU_LAYERS=35
        elif [ "$GPU_MEM" -gt 4000 ]; then
            GPU_LAYERS=20
        else
            GPU_LAYERS=10
        fi
        echo -e "${GREEN}✓${NC} NVIDIA GPU detected: $GPU_INFO"
        echo "  Recommended GPU layers: $GPU_LAYERS"
    fi
elif [ -d "/sys/class/drm" ] && ls /sys/class/drm/card*/device/vendor 2>/dev/null | xargs cat 2>/dev/null | grep -q "0x1002"; then
    GPU_TYPE="rocm"
    echo -e "${GREEN}✓${NC} AMD GPU detected (ROCm)"
elif [ "$(uname)" = "Darwin" ] && sysctl -n machdep.cpu.brand_string 2>/dev/null | grep -q "Apple"; then
    GPU_TYPE="metal"
    echo -e "${GREEN}✓${NC} Apple Silicon detected (Metal)"
else
    echo -e "${YELLOW}!${NC} No GPU detected, using CPU inference"
fi

# Detect RAM
if [ "$(uname)" = "Darwin" ]; then
    RAM_GB=$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))
else
    RAM_GB=$(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024))
fi
echo -e "${GREEN}✓${NC} System RAM: ${RAM_GB}GB"

# Write hardware profile
cat > "$DATA_DIR/hardware_profile.json" << EOF
{
    "gpu_type": "$GPU_TYPE",
    "gpu_layers": $GPU_LAYERS,
    "ram_gb": $RAM_GB,
    "profiled_at": "$(date -Iseconds)"
}
EOF

# === Step 5: Download Models (Optional) ===
echo ""
echo -e "${BLUE}>> [5/6] Model Configuration...${NC}"

if [ "$MODELS_ONLY" = true ] || [ "$WITH_MODELS" = true ]; then
    echo ""
    echo "Hearth Writer works with any GGUF-format model."
    echo ""
    echo "Recommended models based on your hardware ($RAM_GB GB RAM, $GPU_TYPE):"
    
    if [ "$RAM_GB" -ge 16 ]; then
        echo "  → Mistral 7B Instruct Q4_K_M (4.4GB) - Best quality"
        echo "    wget -P models/ https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    elif [ "$RAM_GB" -ge 8 ]; then
        echo "  → Phi-2 Q4_K_M (1.6GB) - Good balance"
        echo "    wget -P models/ https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
    else
        echo "  → TinyLlama Q4_K_M (0.6GB) - Lightweight"
        echo "    wget -P models/ https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    fi
    
    echo ""
    echo "Download manually and place .gguf files in the 'models/' directory"
else
    echo -e "${YELLOW}!${NC} Skipping model download (use --with-models to include)"
    echo "  Place .gguf model files in: $MODEL_DIR/"
fi

# === Step 6: Create Default Configuration ===
echo ""
echo -e "${BLUE}>> [6/6] Creating Default Configuration...${NC}"

# Create default user profile
if [ ! -f "$DATA_DIR/users/default_user.json" ]; then
    cat > "$DATA_DIR/users/default_user.json" << 'EOF'
{
    "user_id": "default",
    "created_at": "2025-01-03T00:00:00",
    "voice_vector": null,
    "stylometry": {
        "avg_sentence_length": 15.0,
        "vocabulary_richness": 0.7,
        "punctuation_density": 0.05,
        "dialogue_ratio": 0.3
    },
    "drift_history": [],
    "last_check": null
}
EOF
    echo -e "${GREEN}✓${NC} Default user profile created"
fi

# Create project manifest if not exists
if [ ! -f "$DATA_DIR/series_db/project/project_manifest.json" ]; then
    cat > "$DATA_DIR/series_db/project/project_manifest.json" << 'EOF'
{
    "project_name": "Untitled Project",
    "version": "1.0.0",
    "archetype": "global_novelist",
    "created_at": "2025-01-03T00:00:00",
    "features": {
        "shadow_nodes": false,
        "visual_tracking": false,
        "logic_locks": false
    }
}
EOF
    echo -e "${GREEN}✓${NC} Project manifest created"
fi

# Make scripts executable
chmod +x setup.sh 2>/dev/null || true
chmod +x start.sh 2>/dev/null || true
chmod +x test_suite.py 2>/dev/null || true

# === Final Message ===
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   INSTALLATION COMPLETE                                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "To start Hearth Writer:"
echo ""
echo "  1. Activate virtual environment:"
echo -e "     ${GREEN}source $ENV_NAME/bin/activate${NC}"
echo ""
echo "  2. (Optional) Set license key for Pro features:"
echo -e "     ${YELLOW}export HEARTH_LICENSE_KEY=\"HRTH_ARCHITECT_yourkey\"${NC}"
echo ""
echo "  3. Start the server:"
echo -e "     ${GREEN}./start.sh${NC}"
echo ""
echo "  4. Open in browser:"
echo -e "     ${BLUE}http://localhost:8000${NC}"
echo ""
echo "Run tests with: python test_suite.py"
echo ""
echo -e "${GREEN}Ready to write.${NC}"
