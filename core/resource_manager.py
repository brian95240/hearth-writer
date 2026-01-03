"""
Hearth Writer Resource Orchestrator
====================================
Manages the "Collapse-to-Zero" architecture with license-aware resource allocation.

Key Principles:
- Idle State: < 100MB RAM (Flask Listener only)
- Active State: ~4GB RAM (Model loaded)
- Cleanup: Auto-purge after 5min inactivity

License Integration:
- Ronin: Single model, no mixing
- Architect: Multi-LORA, Shadow Nodes access
- Showrunner: All features + Team Sync
"""

import multiprocessing
import logging
import time
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .inference_process import InferenceWorker

# Import license validator for feature gating
try:
    from .license_validator import get_validator, can_access_feature
except ImportError:
    # Fallback if license_validator not available
    def can_access_feature(feature): return True
    def get_validator(): return None


class ModelState(Enum):
    COLD = "cold"       # Not loaded
    WARM = "warm"       # Loaded, ready
    HOT = "hot"         # Actively generating
    COOLING = "cooling" # Scheduled for unload


@dataclass
class ModelSlot:
    """Represents a model slot in the orchestrator."""
    name: str
    state: ModelState
    last_used: float
    keep_warm: bool
    memory_mb: int


class ResourceOrchestrator:
    """
    Manages model lifecycle and resource allocation.
    
    Implements the "Collapse-to-Zero" pattern:
    - Models are loaded on-demand
    - Idle models are purged after timeout
    - Memory is returned to OS between operations
    """
    
    # Configuration
    IDLE_TIMEOUT_SECONDS = 300  # 5 minutes
    MAX_CONCURRENT_MODELS = 1   # Ronin limit (increased for Pro)
    
    # Model memory estimates (MB)
    MODEL_MEMORY = {
        "mistral-7b-quantized": 4096,
        "all-MiniLM-L6-v2": 256,
        "coqui-tts": 512,
    }
    
    def __init__(self):
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.worker = None
        
        # Model tracking
        self._model_slots: Dict[str, ModelSlot] = {}
        self._active_locks: Dict[str, bool] = {}
        
        # License-aware limits
        self._update_limits()
    
    def _update_limits(self):
        """Update resource limits based on license tier."""
        validator = get_validator()
        if validator and validator.is_pro():
            self.MAX_CONCURRENT_MODELS = 3  # Pro users can mix models
        else:
            self.MAX_CONCURRENT_MODELS = 1  # Ronin: single model
    
    def _ensure_worker_alive(self):
        """Ensure the inference worker process is running."""
        if self.worker is None or not self.worker.is_alive():
            self.worker = InferenceWorker(self.task_queue, self.result_queue)
            self.worker.start()
            logging.info("Inference Worker spawned (Hot Path activated)")

    def request_model(self, model_name: str, keep_warm: bool = False) -> Optional[Any]:
        """
        Request a model for use.
        
        Args:
            model_name: Name of the model to load
            keep_warm: If True, don't auto-unload after timeout
            
        Returns:
            Model handle (or None if denied by license)
        """
        # Check license for multi-model scenarios
        current_models = len([s for s in self._model_slots.values() if s.state != ModelState.COLD])
        
        if current_models >= self.MAX_CONCURRENT_MODELS:
            if not can_access_feature("multi_lora"):
                logging.warning(f"Model limit reached ({self.MAX_CONCURRENT_MODELS}). Upgrade for Multi-LORA.")
                # Unload oldest model to make room
                self._unload_oldest_model()
        
        # Create or update slot
        if model_name not in self._model_slots:
            self._model_slots[model_name] = ModelSlot(
                name=model_name,
                state=ModelState.COLD,
                last_used=time.time(),
                keep_warm=keep_warm,
                memory_mb=self.MODEL_MEMORY.get(model_name, 1024)
            )
        
        slot = self._model_slots[model_name]
        slot.last_used = time.time()
        slot.keep_warm = keep_warm
        slot.state = ModelState.WARM
        
        # Acquire lock
        self._active_locks[model_name] = True
        
        logging.info(f"Model requested: {model_name} (State: {slot.state.value})")
        return slot  # Return slot as handle
    
    def release_lock(self, model_name: str):
        """
        Release the lock on a model, allowing it to be unloaded.
        
        Args:
            model_name: Name of the model to release
        """
        if model_name in self._active_locks:
            del self._active_locks[model_name]
            
        if model_name in self._model_slots:
            slot = self._model_slots[model_name]
            slot.last_used = time.time()
            
            if not slot.keep_warm:
                slot.state = ModelState.COOLING
                
        logging.debug(f"Lock released: {model_name}")
    
    def _unload_oldest_model(self):
        """Unload the least recently used model."""
        oldest_slot = None
        oldest_time = float('inf')
        
        for name, slot in self._model_slots.items():
            if slot.state != ModelState.COLD and name not in self._active_locks:
                if slot.last_used < oldest_time:
                    oldest_time = slot.last_used
                    oldest_slot = slot
        
        if oldest_slot:
            oldest_slot.state = ModelState.COLD
            logging.info(f"Model unloaded (LRU): {oldest_slot.name}")
    
    def check_idle_models(self):
        """Check for idle models and schedule unload."""
        current_time = time.time()
        
        for name, slot in self._model_slots.items():
            if slot.state in [ModelState.WARM, ModelState.COOLING]:
                if name not in self._active_locks:
                    idle_time = current_time - slot.last_used
                    
                    if idle_time > self.IDLE_TIMEOUT_SECONDS and not slot.keep_warm:
                        slot.state = ModelState.COLD
                        logging.info(f"Model auto-unloaded (idle {idle_time:.0f}s): {name}")

    def generate_text(self, prompt: str, mode: str = "prose", 
                      use_shadow_nodes: bool = False) -> Dict[str, Any]:
        """
        Generate text using the inference worker.
        
        Args:
            prompt: The input text/prompt
            mode: Writing mode (prose, screenplay, comic, etc.)
            use_shadow_nodes: Whether to include shadow node context (Pro feature)
            
        Returns:
            Generation result dictionary
        """
        self._ensure_worker_alive()
        
        # Determine grammar path based on mode
        grammar_path = None
        if mode == "screenplay":
            grammar_path = "./core/grammars/screenplay.gbnf"
        elif mode == "comic":
            # Comic mode requires license check (done in app.py, but defense in depth)
            if not can_access_feature("comic_mode"):
                return {"choices": [{"text": "⚠️ Comic mode requires Architect license."}]}
            grammar_path = "./core/grammars/comic.gbnf"
        
        # Build task
        task = {
            'type': 'generate', 
            'prompt': prompt,
            'grammar_path': grammar_path,
            'mode': mode,
            'use_shadow_nodes': use_shadow_nodes and can_access_feature("shadow_nodes")
        }
        
        self.task_queue.put(task)
        
        # Block until result (or use async in real implementation)
        result = self.result_queue.get()
        
        # Check for idle models after generation
        self.check_idle_models()
        
        return result

    def collapse_to_zero(self, force: bool = False):
        """
        Terminate all resources and return to idle state.
        
        Args:
            force: If True, terminate immediately without cleanup
        """
        # Terminate worker process
        if self.worker and self.worker.is_alive():
            self.task_queue.put({'type': 'poison_pill'})
            self.worker.join(timeout=5)
            
            if self.worker.is_alive():
                self.worker.terminate()
                
            self.worker = None
        
        # Clear model slots
        for slot in self._model_slots.values():
            slot.state = ModelState.COLD
        
        self._active_locks.clear()
        
        logging.info("Collapse to Zero complete. System idle.")
    
    def get_status(self) -> Dict[str, Any]:
        """Return current orchestrator status."""
        return {
            "worker_alive": self.worker is not None and self.worker.is_alive(),
            "active_models": [
                {"name": s.name, "state": s.state.value, "memory_mb": s.memory_mb}
                for s in self._model_slots.values()
                if s.state != ModelState.COLD
            ],
            "active_locks": list(self._active_locks.keys()),
            "max_concurrent": self.MAX_CONCURRENT_MODELS,
            "license_tier": get_validator().get_tier_name() if get_validator() else "unknown"
        }


# Global orchestrator instance
orchestrator = ResourceOrchestrator()
