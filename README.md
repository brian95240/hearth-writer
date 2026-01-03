# Hearth Writer v1.2 "Vertex"

> **The Un-App** — A hyper-efficient, local-first authorship engine with Collapse-to-Zero architecture.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Philosophy

Hearth Writer rejects cloud dependencies in favor of **Privacy Absolute**. Your words never leave your machine.

**Core Principles:**
- **Collapse-to-Zero**: < 100MB RAM when idle, ~4GB only during active generation
- **Synergistic Cascading**: Zero-latency mode switching via intent detection
- **Defense in Depth**: Multiple license validation points
- **GIL-Free**: AI inference runs in isolated process

---

## The 7 Archetypes

| Archetype | Critical Need | Hearth Solution |
|-----------|---------------|-----------------|
| **Comic Architect** | Visual continuity across issues | Visual Tag Injection |
| **Global Novelist** | Deep narrative callback (1000+ pages) | Shadow Nodes |
| **Children's Author** | Simple vocabulary (Age 6-8) | Lexile Grammar |
| **Screenwriter** | Rapid formatting & flow | Intent Router |
| **TV Showrunner** | Arc dependencies across seasons | Logic Locks |
| **Playwright** | Lyrics vs. Dialogue vs. Blocking | Stage Mode |
| **Game Designer** | Branching logic (IF/ELSE) | Logic Nodes |

---

## Quick Start

### One-Line Install (Linux/macOS)

```bash
curl -sSL https://raw.githubusercontent.com/brian95240/hearth-writer/main/setup.sh | bash
```

### Manual Install

```bash
# Clone repository
git clone https://github.com/brian95240/hearth-writer.git
cd hearth-writer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download models (optional - for full functionality)
./setup.sh --models-only

# Start the server
./start.sh
```

### Verify Installation

```bash
python test_suite.py
```

---

## License Tiers

### Ronin (Free - AGPLv3)
- Local storage only
- Prose & Screenplay modes
- Voice Engine (cached TTS)
- Linear timeline

### Architect ($19/mo)
- Commercial license
- **Shadow Nodes** (complex plots)
- **Visual Tagging** (comics)
- Multi-LORA mixing
- Timeline injection

### Showrunner ($49/seat)
- Enterprise license
- Team Sync & Collaboration
- White labeling
- Legal indemnity
- Custom grammar files

### Activate License

```bash
export HEARTH_LICENSE_KEY="HRTH_ARCHITECT_YOUR_KEY"
./start.sh
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HEARTH WRITER v1.2                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   app.py    │  │   Intent    │  │   License   │         │
│  │ (Gatekeeper)│──│   Router    │──│  Validator  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MULTIPROCESSING WALL                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  Inference  │  │   Context   │  │    Voice    │  │   │
│  │  │   Worker    │  │   Engine    │  │   Engine    │  │   │
│  │  │  (GIL-Free) │  │    (RAG)    │  │  (Cached)   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 DATA LAYER                           │   │
│  │  series_db/  │  cache/  │  users/  │  grammars/     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
hearth_writer/
├── app.py                    # Main API (Gatekeeper)
├── requirements.txt          # Pinned dependencies
├── setup.sh                  # Environment installer
├── start.sh                  # Process launcher
├── test_suite.py             # Diagnostic tests
│
├── core/                     # Logic Core
│   ├── __init__.py
│   ├── context_engine.py     # RAG & Shadow Nodes
│   ├── inference_process.py  # GIL-Free AI worker
│   ├── license_validator.py  # Defense in Depth
│   ├── pure_mode.py          # Voice drift detection
│   ├── resource_manager.py   # Collapse-to-Zero
│   ├── silent_listener.py    # Background analysis
│   ├── voice_engine.py       # TTS with caching
│   └── grammars/
│       ├── screenplay.gbnf
│       ├── comic.gbnf
│       ├── playwright.gbnf
│       └── lexile_simple.gbnf
│
├── data/
│   ├── cache/                # Transient cache
│   ├── schemas/              # System definitions
│   ├── series_db/            # Long-term memory
│   └── users/                # User profiles
│
├── frontend/
│   └── public/
│       ├── index.html        # Landing page
│       ├── welcome_architect.html
│       └── welcome_showrunner.html
│
├── logs/                     # Runtime logs
├── models/                   # GGUF model files
└── sync/                     # P2P sync protocol
```

---

## API Reference

### WebSocket Endpoint

```
ws://localhost:8000/hearth_stream
```

### Actions

**Generate Text:**
```json
{"action": "generate", "text": "INT. BATCAVE - NIGHT"}
```

**Speak Text:**
```json
{"action": "speak", "text": "Hello, writer."}
```

### Voice Commands

```
system: switch to screenplay
system: switch to comic mode
system: enable shadow nodes
system: status
system: collapse
```

### Implicit Detection

The Intent Router automatically detects:
- `INT.` / `EXT.` → Screenplay mode
- `PAGE 1` / `PANEL 1` → Comic mode
- `ACT I` / `SCENE 1` → Playwright mode

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HEARTH_LICENSE_KEY` | License key for Pro features | (none) |
| `HEARTH_USE_GPU` | Enable GPU acceleration | `0` |
| `HEARTH_TTS_GPU` | Enable GPU for TTS | `0` |

### Project Manifest

Edit `data/series_db/project/project_manifest.json` to configure:
- Active archetype
- Feature toggles
- Series metadata
- Visual states (Comic mode)
- Shadow nodes (Pro)
- Logic locks (Showrunner)

---

## Development

### Run Tests

```bash
python test_suite.py
```

### Code Style

```bash
pip install black
black .
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## Troubleshooting

### Model Not Found

```bash
# Download models manually
./setup.sh --models-only
```

### Port Already in Use

```bash
# Kill existing process
pkill -f "python.*app.py"
./start.sh
```

### License Not Recognized

```bash
# Verify key format
echo $HEARTH_LICENSE_KEY
# Should start with HRTH_ARCHITECT_ or HRTH_SHOWRUNNER_
```

---

## Changelog

### v1.2.0 "Vertex" (2025-01-03)
- Added tiered licensing (Ronin/Architect/Showrunner)
- Implemented Defense in Depth validation
- Added Comic, Playwright, Children's grammar files
- Enhanced Collapse-to-Zero with lazy loading
- Added Logic Locks for arc dependencies
- Improved test suite with closed-loop diagnostics

### v1.1.0 (Previous)
- Initial Shadow Nodes implementation
- Voice Engine with LRU caching
- Intent Router for mode switching

---

## License

**Ronin Tier:** GNU Affero General Public License v3.0

**Architect/Showrunner Tiers:** Commercial License (see purchase page)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/brian95240/hearth-writer/issues)
- **Documentation:** [Wiki](https://github.com/brian95240/hearth-writer/wiki)
- **Enterprise:** enterprise@hearthwriter.dev

---

*Built for creators who refuse to compromise.*
