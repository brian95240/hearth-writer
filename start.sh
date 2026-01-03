#!/bin/bash
# Hearth Writer v1.2 "Vertex" - Start Script
# Usage: ./start.sh [--dev] [--port PORT] [--no-daemon] [--simple]

# === Configuration ===
ENV_NAME="hearth_env"
HOST="127.0.0.1"
API_PORT="8000"
UI_PORT="3000"
LOG_DIR="./logs"

# ANSI Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# === Parse Arguments ===
DEV_MODE=false
NO_DAEMON=false
SIMPLE_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --port)
            API_PORT="$2"
            shift 2
            ;;
        --no-daemon)
            NO_DAEMON=true
            shift
            ;;
        --simple)
            SIMPLE_MODE=true
            shift
            ;;
        --help)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dev         Enable development mode (auto-reload)"
            echo "  --port PORT   Set API server port (default: 8000)"
            echo "  --no-daemon   Skip starting the Silent Listener daemon"
            echo "  --simple      Simple mode: only start API (no UI, no daemon)"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# === Banner ===
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   HEARTH WRITER v1.2 \"VERTEX\"                                 ║"
echo "║   Collapse-to-Zero Architecture | Privacy Absolute            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# === Pre-Flight Checks ===
mkdir -p $LOG_DIR

# Check for virtual environment
if [ -d "$ENV_NAME" ]; then
    source $ENV_NAME/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment: $ENV_NAME"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment: venv"
else
    echo -e "${YELLOW}!${NC} No virtual environment found, using system Python"
fi

# === License Check ===
if [ -n "$HEARTH_LICENSE_KEY" ]; then
    if [[ "$HEARTH_LICENSE_KEY" == HRTH_SHOWRUNNER_* ]]; then
        echo -e "${GREEN}✓${NC} License: ${CYAN}SHOWRUNNER${NC} (Enterprise)"
    elif [[ "$HEARTH_LICENSE_KEY" == HRTH_ARCHITECT_* ]]; then
        echo -e "${GREEN}✓${NC} License: ${YELLOW}ARCHITECT${NC} (Pro)"
    else
        echo -e "${YELLOW}!${NC} License: Invalid key format, defaulting to RONIN"
    fi
else
    echo -e "${BLUE}ℹ${NC} License: RONIN (Free)"
    echo "  Set HEARTH_LICENSE_KEY for Pro features"
fi

# === Model Check ===
MODEL_COUNT=$(find ./models -name "*.gguf" 2>/dev/null | wc -l)
if [ "$MODEL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}!${NC} No .gguf models found in ./models/"
    echo "  Run: ./setup.sh --with-models"
else
    echo -e "${GREEN}✓${NC} Found $MODEL_COUNT model(s)"
fi

echo ""

# === Process Management (The Trap) ===
# Ensures Ctrl+C kills all components and triggers collapse-to-zero
cleanup() {
    echo -e "\n${RED}>> Extinguishing Hearth...${NC}"
    
    # Kill all spawned processes
    [ -n "$PID_API" ] && kill $PID_API 2>/dev/null
    [ -n "$PID_UI" ] && kill $PID_UI 2>/dev/null
    [ -n "$PID_DAEMON" ] && kill $PID_DAEMON 2>/dev/null
    
    # Force collapse-to-zero on exit
    python -c "
try:
    from core.resource_manager import ResourceOrchestrator
    ResourceOrchestrator().collapse_to_zero(force=True)
    print('Resources released.')
except Exception as e:
    pass
" 2>/dev/null
    
    echo -e "${GREEN}Hearth extinguished. Goodbye.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# === Simple Mode (API Only) ===
if [ "$SIMPLE_MODE" = true ]; then
    echo -e "${CYAN}>> Starting in Simple Mode (API only)...${NC}"
    echo ""
    echo "WebSocket: ws://$HOST:$API_PORT/hearth_stream"
    echo "Health:    http://$HOST:$API_PORT/health"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    
    if [ "$DEV_MODE" = true ]; then
        export FLASK_ENV=development
        export FLASK_DEBUG=1
    fi
    
    python app.py
    exit 0
fi

# === Full Mode: Launch All Components ===

# A. The Core (Flask API + WebSocket)
echo -e "${GREEN}>> [1/3] Starting Inference Engine (Port $API_PORT)...${NC}"

if [ "$DEV_MODE" = true ]; then
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    python app.py &
    PID_API=$!
else
    # Check if gunicorn is available for production
    if command -v gunicorn &> /dev/null; then
        gunicorn -w 1 -k flask_sock.workers.GeeWorker \
            -b $HOST:$API_PORT app:app \
            --access-logfile "$LOG_DIR/access.log" \
            --error-logfile "$LOG_DIR/error.log" &
        PID_API=$!
    else
        # Fallback to Flask development server
        python app.py &
        PID_API=$!
    fi
fi

# Wait for API warm-up
echo "   Waiting for warm-up..."
sleep 2

# B. The Silent Listener (Trend/Context Daemon)
if [ "$NO_DAEMON" = false ]; then
    echo -e "${GREEN}>> [2/3] Waking Silent Listener (Daemon)...${NC}"
    nice -n 10 python -m core.silent_listener \
        --interval 3600 \
        --sources "rss_feeds.json" \
        >> "$LOG_DIR/daemon.log" 2>&1 &
    PID_DAEMON=$!
else
    echo -e "${YELLOW}>> [2/3] Silent Listener skipped (--no-daemon)${NC}"
fi

# C. The Interface (Frontend)
echo -e "${GREEN}>> [3/3] Checking Frontend...${NC}"

if [ -d "frontend/build" ]; then
    cd frontend
    if command -v npx &> /dev/null; then
        npx serve -s build -l $UI_PORT &
        PID_UI=$!
        cd ..
        UI_RUNNING=true
    else
        cd ..
        UI_RUNNING=false
        echo -e "${YELLOW}   npx not found, serving static files via API${NC}"
    fi
elif [ -d "frontend/public" ]; then
    # Serve static files directly
    echo -e "${YELLOW}   No build found, using static files${NC}"
    UI_RUNNING=false
else
    echo -e "${YELLOW}   No frontend found${NC}"
    UI_RUNNING=false
fi

# === Steady State ===
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   HEARTH IS BURNING                                           ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "   ${GREEN}API:${NC}      http://$HOST:$API_PORT"
echo -e "   ${GREEN}WebSocket:${NC} ws://$HOST:$API_PORT/hearth_stream"
echo -e "   ${GREEN}Health:${NC}   http://$HOST:$API_PORT/health"

if [ "$UI_RUNNING" = true ]; then
    echo -e "   ${GREEN}UI:${NC}       http://$HOST:$UI_PORT"
fi

if [ -n "$PID_DAEMON" ]; then
    echo -e "   ${GREEN}Daemon:${NC}   Active (PID $PID_DAEMON)"
fi

echo ""
echo -e "   ${YELLOW}[Press Ctrl+C to stop]${NC}"
echo ""

# Keep script running to maintain the trap
wait
