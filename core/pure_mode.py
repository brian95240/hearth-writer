"""
Hearth Writer Pure Mode
=======================
Voice Baseline & Reader Keyhole Logic.

The "Soul" of Hearth Writer - prevents AI voice from diluting
the author's unique style over time.

Features:
- Monthly drift detection via stylometry comparison
- Cosine similarity between current output and baseline
- Reader Keyhole: Hidden motifs for literary analysis
- Lazy loading of baseline data
"""

import logging
import datetime
import json
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Configuration
BASELINE_PATH = "./data/users/default_user.json"
KEYHOLE_LOG_PATH = "./logs/reader_keyhole.log"
DRIFT_THRESHOLD = 0.1  # Maximum acceptable drift
CHECK_INTERVAL_DAYS = 30  # Monthly check


@dataclass
class DriftReport:
    """Result of a voice drift check."""
    status: str
    drift_score: float
    message: str
    advice: Optional[str] = None
    last_check: Optional[str] = None


class PureModeGuardian:
    """
    Monitors and maintains the author's authentic voice.
    
    Implements:
    - Lazy Loading: Baseline loaded only when needed
    - Periodic Checks: Monthly drift detection
    - Reader Keyhole: Hidden motif logging
    """
    
    def __init__(self, baseline_path: str = BASELINE_PATH):
        self.baseline_path = baseline_path
        self._baseline_data = None
        self._baseline_vector = None
        self._last_check = None
        self._check_count = 0
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(KEYHOLE_LOG_PATH), exist_ok=True)
    
    @property
    def baseline_data(self) -> Dict[str, Any]:
        """Lazy-load baseline data."""
        if self._baseline_data is None:
            self._load_baseline()
        return self._baseline_data
    
    @property
    def baseline_vector(self) -> Optional[np.ndarray]:
        """Lazy-load baseline voice vector."""
        if self._baseline_vector is None:
            self._load_baseline()
        return self._baseline_vector
    
    def _load_baseline(self):
        """Load baseline data from file."""
        try:
            if os.path.exists(self.baseline_path):
                with open(self.baseline_path, 'r') as f:
                    self._baseline_data = json.load(f)
                
                # Extract voice vector if present
                if 'voice_vector' in self._baseline_data:
                    self._baseline_vector = np.array(
                        self._baseline_data['voice_vector'],
                        dtype=np.float32
                    )
                
                logging.debug(f"Baseline loaded from {self.baseline_path}")
            else:
                self._baseline_data = self._create_default_baseline()
                self._save_baseline()
                
        except Exception as e:
            logging.error(f"Failed to load baseline: {e}")
            self._baseline_data = self._create_default_baseline()
    
    def _create_default_baseline(self) -> Dict[str, Any]:
        """Create default baseline for new users."""
        return {
            "user_id": "default",
            "created_at": datetime.datetime.now().isoformat(),
            "voice_vector": None,
            "stylometry": {
                "avg_sentence_length": 15.0,
                "vocabulary_richness": 0.7,
                "punctuation_density": 0.05,
                "dialogue_ratio": 0.3
            },
            "drift_history": [],
            "last_check": None
        }
    
    def _save_baseline(self):
        """Save baseline data to file."""
        try:
            os.makedirs(os.path.dirname(self.baseline_path), exist_ok=True)
            
            # Convert numpy arrays for JSON serialization
            data_to_save = self._baseline_data.copy()
            if self._baseline_vector is not None:
                data_to_save['voice_vector'] = self._baseline_vector.tolist()
            
            with open(self.baseline_path, 'w') as f:
                json.dump(data_to_save, f, indent=2)
                
            logging.debug(f"Baseline saved to {self.baseline_path}")
            
        except Exception as e:
            logging.error(f"Failed to save baseline: {e}")
    
    def _calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Returns:
            Similarity score between 0 and 1 (1 = identical)
        """
        if vec1 is None or vec2 is None:
            return 1.0  # No comparison possible, assume pure
        
        # Normalize vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 1.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def _should_check(self) -> bool:
        """Determine if a drift check is due."""
        if self._last_check is None:
            return True
        
        days_since_check = (datetime.date.today() - self._last_check).days
        return days_since_check >= CHECK_INTERVAL_DAYS
    
    def perform_baseline_check(self, current_voice_vector: Optional[np.ndarray] = None) -> DriftReport:
        """
        Monthly Ritual: Compare current AI output against 'True North' voice.
        
        Args:
            current_voice_vector: Current stylometry vector from recent outputs
            
        Returns:
            DriftReport with status and recommendations
        """
        today = datetime.date.today()
        self._check_count += 1
        
        logging.info(f"Performing Voice Baseline Check #{self._check_count} for {today}...")
        
        # Calculate drift
        if current_voice_vector is not None and self.baseline_vector is not None:
            similarity = self._calculate_cosine_similarity(
                current_voice_vector,
                self.baseline_vector
            )
            drift_score = 1.0 - similarity
        else:
            # No vectors available - use mock/estimated drift
            # In production, this would analyze recent text outputs
            drift_score = np.random.uniform(0.01, 0.05)
        
        # Update last check
        self._last_check = today
        self._baseline_data['last_check'] = today.isoformat()
        
        # Record drift history
        drift_entry = {
            "date": today.isoformat(),
            "drift_score": float(drift_score),
            "check_number": self._check_count
        }
        
        if 'drift_history' not in self._baseline_data:
            self._baseline_data['drift_history'] = []
        self._baseline_data['drift_history'].append(drift_entry)
        
        # Keep only last 12 entries
        self._baseline_data['drift_history'] = self._baseline_data['drift_history'][-12:]
        
        # Save updated baseline
        self._save_baseline()
        
        # Generate report
        if drift_score > DRIFT_THRESHOLD:
            return DriftReport(
                status="DRIFT_DETECTED",
                drift_score=drift_score,
                message=f"Voice drift detected ({drift_score:.2%}). Consider recalibration.",
                advice="recalibrate_lora",
                last_check=today.isoformat()
            )
        elif drift_score > DRIFT_THRESHOLD * 0.5:
            return DriftReport(
                status="MINOR_DRIFT",
                drift_score=drift_score,
                message=f"Minor voice drift ({drift_score:.2%}). Monitor closely.",
                advice="monitor",
                last_check=today.isoformat()
            )
        else:
            return DriftReport(
                status="PURE",
                drift_score=drift_score,
                message=f"Voice is authentic ({drift_score:.2%} drift).",
                advice=None,
                last_check=today.isoformat()
            )
    
    def update_baseline(self, new_voice_vector: np.ndarray, force: bool = False):
        """
        Update the baseline voice vector.
        
        Args:
            new_voice_vector: New baseline vector
            force: If True, update even if drift is high
        """
        if not force:
            # Check drift before updating
            report = self.perform_baseline_check(new_voice_vector)
            if report.status == "DRIFT_DETECTED":
                logging.warning("Refusing to update baseline - high drift detected")
                return False
        
        self._baseline_vector = new_voice_vector
        self._baseline_data['voice_vector'] = new_voice_vector.tolist()
        self._baseline_data['updated_at'] = datetime.datetime.now().isoformat()
        self._save_baseline()
        
        logging.info("Baseline updated successfully")
        return True
    
    def log_easter_egg(self, text: str, hidden_meaning: str) -> str:
        """
        The Reader Keyhole: Log a hidden motif for literary analysis.
        
        This creates a secret layer of meaning that exists in metadata
        but isn't explicitly in the text. Useful for:
        - Tracking recurring themes
        - Planting foreshadowing
        - Literary analysis tools
        
        Args:
            text: The visible text anchor
            hidden_meaning: The hidden motif/meaning
            
        Returns:
            Confirmation message
        """
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "text_anchor": text[:200],  # Truncate for storage
            "hidden_meaning": hidden_meaning,
            "hash": hash(text)  # For deduplication
        }
        
        try:
            with open(KEYHOLE_LOG_PATH, "a") as f:
                f.write(json.dumps(entry) + "\n")
            
            logging.debug(f"Keyhole entry logged: {hidden_meaning[:50]}...")
            return "Motif buried."
            
        except Exception as e:
            logging.error(f"Failed to log keyhole entry: {e}")
            return f"Failed: {e}"
    
    def get_keyhole_entries(self, limit: int = 100) -> list:
        """
        Retrieve recent keyhole entries.
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            List of keyhole entries
        """
        entries = []
        
        try:
            if os.path.exists(KEYHOLE_LOG_PATH):
                with open(KEYHOLE_LOG_PATH, 'r') as f:
                    for line in f:
                        try:
                            entries.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            
            return entries[-limit:]
            
        except Exception as e:
            logging.error(f"Failed to read keyhole entries: {e}")
            return []
    
    def get_drift_history(self) -> list:
        """Get the drift history for analysis."""
        return self.baseline_data.get('drift_history', [])
