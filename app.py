"""
Hearth Writer v1.2 "Vertex" - Main Application
===============================================
The Gatekeeper: License-aware API with Collapse-to-Zero architecture.

Design Principles:
- Lazy Loading: Resources loaded only when needed
- Collapse-to-Zero: Idle state < 100MB RAM
- Defense in Depth: Multiple license validation points
- GIL-Free: AI inference in separate process

Author: Hearth Writer Team
License: AGPLv3 (Ronin) / Commercial (Architect/Showrunner)
"""

import logging
import json
import signal
import sys
import re
import os
from typing import Tuple, Optional, Any

from flask import Flask
from flask_sock import Sock

# === LAZY IMPORTS ===
# Core modules are imported lazily to minimize startup footprint
_orchestrator = None
_voice_engine = None

def get_orchestrator():
    """Lazy-load the ResourceOrchestrator (Collapse-to-Zero pattern)."""
    global _orchestrator
    if _orchestrator is None:
        from core.resource_manager import ResourceOrchestrator
        _orchestrator = ResourceOrchestrator()
        logging.info("ResourceOrchestrator initialized (lazy)")
    return _orchestrator

def get_voice_engine():
    """Lazy-load the VoiceEngine (only when TTS is requested)."""
    global _voice_engine
    if _voice_engine is None:
        from core.voice_engine import VoiceEngine
        _voice_engine = VoiceEngine()
        logging.info("VoiceEngine initialized (lazy)")
    return _voice_engine

# === Configuration ===
app = Flask(__name__)
sock = Sock(app)

# Suppress Flask's verbose logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Configure application logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - HEARTH - %(levelname)s - %(message)s'
)

# === LICENSING LOGIC (The Gatekeeper) ===

def get_license_tier() -> str:
    """
    Checks for a valid license key in the environment.
    
    Tier Hierarchy:
    - ronin: Free tier (AGPLv3)
    - architect: Pro tier ($19/mo)
    - showrunner: Enterprise tier ($49/seat)
    
    In v1.2, this is a simple prefix check.
    In v2.0+, this would validate against a license server.
    """
    key = os.environ.get("HEARTH_LICENSE_KEY", "")
    
    if not key:
        return "ronin"
    
    # Validate key format
    if key.startswith("HRTH_SHOWRUNNER_"):
        return "showrunner"
    if key.startswith("HRTH_ARCHITECT_"):
        return "architect"
    
    # Invalid key format defaults to free tier
    return "ronin"


def check_feature_access(feature_name: str) -> Tuple[bool, str]:
    """
    Validates if current license tier can access a feature.
    
    Args:
        feature_name: The feature to check
        
    Returns:
        Tuple of (allowed: bool, message: str)
    """
    tier = get_license_tier()
    
    # Feature -> Required Tier mapping
    FEATURE_REQUIREMENTS = {
        "shadow_nodes": ["architect", "showrunner"],
        "visual_tracking": ["architect", "showrunner"],
        "multi_lora": ["architect", "showrunner"],
        "comic_mode": ["architect", "showrunner"],
        "collaboration": ["showrunner"],
        "team_sync": ["showrunner"],
    }
    
    # Denial messages
    DENIAL_MESSAGES = {
        "shadow_nodes": "⚠️ FEATURE LOCKED: Shadow Nodes & Timeline Injection require the 'Architect' License.",
        "visual_tracking": "⚠️ FEATURE LOCKED: Visual Tagging requires the 'Architect' License.",
        "multi_lora": "⚠️ FEATURE LOCKED: Multi-LORA Mixing requires the 'Architect' License.",
        "comic_mode": "⚠️ FEATURE LOCKED: Comic/Marvel Mode requires the 'Architect' License.",
        "collaboration": "⚠️ FEATURE LOCKED: Team Sync requires the 'Showrunner' License.",
        "team_sync": "⚠️ FEATURE LOCKED: Team Sync requires the 'Showrunner' License.",
    }
    
    required_tiers = FEATURE_REQUIREMENTS.get(feature_name, [])
    
    # If feature not in requirements, allow by default
    if not required_tiers:
        return True, "Access Granted"
    
    if tier in required_tiers:
        return True, "Access Granted"
    
    return False, DENIAL_MESSAGES.get(feature_name, f"⚠️ FEATURE LOCKED: {feature_name} requires upgrade.")


# === INTENT ROUTER (Synergistic Cascade) ===

def parse_intent(text: str) -> Tuple[bool, str, Optional[str]]:
    """
    Parses user input for intent before touching GPU resources.
    
    This is the "Synergistic Cascade" - zero-latency mode switching
    by detecting intent patterns before invoking heavy inference.
    
    Args:
        text: User's input text
        
    Returns:
        Tuple of (is_command: bool, intent: str, metadata: Optional[str])
    """
    text_lower = text.lower().strip()
    
    # 1. Voice/Explicit Command Triggers
    if text_lower.startswith("system:") or text_lower.startswith("computer,"):
        
        # Mode Switching
        if "switch to" in text_lower:
            # Comic mode (Pro feature)
            if "comic" in text_lower or "marvel" in text_lower:
                allowed, msg = check_feature_access("comic_mode")
                if not allowed:
                    return True, "denial", msg
                return True, "switch_mode", "comic"
            
            # Screenplay mode (Free)
            if "screenplay" in text_lower:
                return True, "switch_mode", "screenplay"
            
            # Playwright mode (Free)
            if "playwright" in text_lower or "stage" in text_lower:
                return True, "switch_mode", "playwright"
            
            # Children's mode (Free)
            if "children" in text_lower or "kids" in text_lower:
                return True, "switch_mode", "children"
            
            # Game mode (Pro feature)
            if "game" in text_lower:
                allowed, msg = check_feature_access("shadow_nodes")  # Uses same tier
                if not allowed:
                    return True, "denial", msg
                return True, "switch_mode", "game"
            
            # Default prose
            if "prose" in text_lower or "novel" in text_lower:
                return True, "switch_mode", "prose"
        
        # Feature Toggles
        if "enable shadow nodes" in text_lower:
            allowed, msg = check_feature_access("shadow_nodes")
            if not allowed:
                return True, "denial", msg
            return True, "toggle_feature", "shadow_nodes"
        
        if "enable visual tracking" in text_lower:
            allowed, msg = check_feature_access("visual_tracking")
            if not allowed:
                return True, "denial", msg
            return True, "toggle_feature", "visual_tracking"
        
        if "enable collaboration" in text_lower or "enable team" in text_lower:
            allowed, msg = check_feature_access("collaboration")
            if not allowed:
                return True, "denial", msg
            return True, "toggle_feature", "collaboration"
        
        # Status check
        if "status" in text_lower:
            return True, "status", None
        
        # Collapse to zero
        if "collapse" in text_lower or "shutdown" in text_lower:
            return True, "collapse", None

    # 2. Implicit Context Triggers (Auto-detection)
    # Screenplay format detection
    if re.match(r'^(INT\.|EXT\.|EST\.)', text.strip()):
        return False, "implicit_switch", "screenplay"
    
    # Comic panel detection
    if re.match(r'^(PAGE\s+\d+|PANEL\s+\d+)', text.strip(), re.IGNORECASE):
        allowed, _ = check_feature_access("comic_mode")
        if allowed:
            return False, "implicit_switch", "comic"
    
    # Playwright detection
    if re.match(r'^(ACT\s+[IVX]+|SCENE\s+\d+)', text.strip(), re.IGNORECASE):
        return False, "implicit_switch", "playwright"
    
    # Default: No command, just write
    return False, "write", None


# === WebSocket Routes ===

@sock.route('/hearth_stream')
def hearth_stream(ws):
    """
    Main WebSocket endpoint for real-time writing assistance.
    
    Protocol:
    - Client sends: {"action": "generate", "text": "..."}
    - Server sends: {"type": "text_delta", "content": "..."}
    """
    tier = get_license_tier()
    logging.info(f"Client connected. License Tier: {tier.upper()}")
    
    current_mode = "prose"
    shadow_nodes_enabled = False
    visual_tracking_enabled = False
    
    try:
        while True:
            data = ws.receive()
            if not data:
                break
            
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                ws.send(json.dumps({"type": "error", "content": "Invalid JSON"}))
                continue
            
            action = payload.get("action")
            
            # === GENERATE ACTION ===
            if action == "generate":
                user_text = payload.get("text", "")
                
                # A. Run Intent Check (Zero-latency)
                is_cmd, intent, meta = parse_intent(user_text)
                
                if is_cmd:
                    if intent == "denial":
                        # Send upgrade upsell
                        ws.send(json.dumps({
                            "type": "system_event",
                            "event": "feature_locked",
                            "content": meta
                        }))
                        continue
                    
                    if intent == "switch_mode":
                        current_mode = meta
                        ws.send(json.dumps({
                            "type": "system_event",
                            "event": "mode_switch",
                            "content": f"Switched to {meta.upper()} mode."
                        }))
                        continue
                    
                    if intent == "toggle_feature":
                        if meta == "shadow_nodes":
                            shadow_nodes_enabled = True
                            ws.send(json.dumps({
                                "type": "system_event",
                                "event": "feature_enabled",
                                "content": "Shadow Nodes enabled. Open loops will be tracked."
                            }))
                        elif meta == "visual_tracking":
                            visual_tracking_enabled = True
                            ws.send(json.dumps({
                                "type": "system_event",
                                "event": "feature_enabled",
                                "content": "Visual Tracking enabled. Entity states will persist."
                            }))
                        continue
                    
                    if intent == "status":
                        orchestrator = get_orchestrator()
                        status = orchestrator.get_status()
                        status["current_mode"] = current_mode
                        status["shadow_nodes"] = shadow_nodes_enabled
                        status["visual_tracking"] = visual_tracking_enabled
                        ws.send(json.dumps({
                            "type": "status",
                            "content": status
                        }))
                        continue
                    
                    if intent == "collapse":
                        orchestrator = get_orchestrator()
                        orchestrator.collapse_to_zero(force=True)
                        ws.send(json.dumps({
                            "type": "system_event",
                            "event": "collapsed",
                            "content": "System collapsed to zero. Resources released."
                        }))
                        continue
                
                elif intent == "implicit_switch":
                    if current_mode != meta:
                        current_mode = meta
                        ws.send(json.dumps({
                            "type": "meta",
                            "status": f"Auto-switched to {meta.upper()} mode"
                        }))
                
                # B. Generation Loop (Lazy-load orchestrator)
                ws.send(json.dumps({"type": "meta", "status": "processing"}))
                
                orchestrator = get_orchestrator()
                response = orchestrator.generate_text(
                    user_text,
                    mode=current_mode,
                    use_shadow_nodes=shadow_nodes_enabled
                )
                
                # Extract generated text
                generated_text = ""
                if "choices" in response and response["choices"]:
                    generated_text = response["choices"][0].get("text", "")
                elif "error" in response:
                    generated_text = f"[Error: {response['error']}]"
                
                ws.send(json.dumps({
                    "type": "text_delta",
                    "content": generated_text
                }))
            
            # === SPEAK ACTION ===
            elif action == "speak":
                text_to_speak = payload.get("text", "")
                
                if not text_to_speak:
                    continue
                
                # Lazy-load voice engine
                import numpy as np
                voice_engine = get_voice_engine()
                
                # Use default voice vector (or load from user profile)
                voice_vec = np.zeros(512, dtype=np.float32)
                
                path = voice_engine.synthesize(text_to_speak, voice_vec)
                ws.send(json.dumps({
                    "type": "audio_event",
                    "path": path
                }))
            
            # === UNKNOWN ACTION ===
            else:
                ws.send(json.dumps({
                    "type": "error",
                    "content": f"Unknown action: {action}"
                }))
    
    except Exception as e:
        logging.error(f"Stream Error: {e}")
        try:
            ws.send(json.dumps({"type": "error", "content": str(e)}))
        except:
            pass
    
    finally:
        logging.info("Client disconnected.")


# === Health Check Route ===

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    return json.dumps({
        "status": "healthy",
        "version": "1.2.0",
        "codename": "Vertex",
        "tier": get_license_tier()
    }), 200, {'Content-Type': 'application/json'}


# === Graceful Shutdown ===

def handle_shutdown(sig, frame):
    """Handle SIGINT/SIGTERM for graceful shutdown."""
    logging.info(f"Received signal {sig}. Initiating graceful shutdown...")
    
    global _orchestrator
    if _orchestrator is not None:
        _orchestrator.collapse_to_zero(force=True)
    
    logging.info("Shutdown complete.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


# === Frontend Static File Serving ===

from flask import send_from_directory

@app.route('/')
def serve_index():
    """Serve the main frontend page."""
    return send_from_directory('frontend/public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from frontend/public, fallback to index.html."""
    if os.path.exists(os.path.join('frontend/public', path)):
        return send_from_directory('frontend/public', path)
    return send_from_directory('frontend/public', 'index.html')


# === Main Entry Point ===

if __name__ == '__main__':
    # Display startup banner
    print("""
    ╔═══════════════════════════════════════════╗
    ║   HEARTH WRITER v1.2 "VERTEX"             ║
    ║   Collapse-to-Zero Architecture           ║
    ║   Privacy Absolute | Local-First          ║
    ╚═══════════════════════════════════════════╝
    """)
    
    tier = get_license_tier()
    logging.info(f"Starting with License Tier: {tier.upper()}")
    logging.info("WebSocket endpoint: ws://localhost:8000/hearth_stream")
    logging.info("Health check: http://localhost:8000/health")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
