"""
Hearth Writer Silent Listener
=============================
Background daemon for trend analysis and context injection.

Features:
- Periodic scanning of external sources (RSS, APIs)
- Logic Locks: Prevents killing characters needed for future arcs
- Context Cache: File-based IPC with main application
- Lazy resource usage: Only active when scheduled

This is the "TV Showrunner" feature - tracks arc dependencies
across seasons and flags potential continuity conflicts.
"""

import time
import argparse
import logging
import json
import os
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Configuration
CONTEXT_CACHE_PATH = "./data/context_cache.json"
LOGIC_LOCKS_PATH = "./data/series_db/project/logic_locks.json"
DEFAULT_INTERVAL = 3600  # 1 hour

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - LISTENER - %(levelname)s - %(message)s'
)


@dataclass
class TrendContext:
    """Detected trend for context injection."""
    trend: str
    relevance_score: float
    source: str
    timestamp: float


@dataclass
class LogicLock:
    """A protected entity that cannot be removed from the narrative."""
    entity_name: str
    reason: str
    future_chapter: str
    locked_until: Optional[str] = None


class SilentListener:
    """
    Background daemon for trend analysis and arc dependency tracking.
    
    Implements:
    - Lazy Loading: Resources loaded only when needed
    - File-based IPC: Communicates via JSON files
    - Logic Locks: Prevents continuity errors
    """
    
    def __init__(self, sources_file: str = "rss.json"):
        self.sources_file = sources_file
        self._sources = None
        self._logic_locks: List[LogicLock] = []
        self._last_scan = None
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(CONTEXT_CACHE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(LOGIC_LOCKS_PATH), exist_ok=True)
    
    @property
    def sources(self) -> List[Dict[str, str]]:
        """Lazy-load RSS/API sources."""
        if self._sources is None:
            self._load_sources()
        return self._sources
    
    def _load_sources(self):
        """Load external sources configuration."""
        try:
            if os.path.exists(self.sources_file):
                with open(self.sources_file, 'r') as f:
                    self._sources = json.load(f)
            else:
                # Default sources
                self._sources = [
                    {"type": "mock", "name": "Literary Trends", "url": None},
                    {"type": "mock", "name": "Genre Analysis", "url": None}
                ]
                
        except Exception as e:
            logging.error(f"Failed to load sources: {e}")
            self._sources = []
    
    def _load_logic_locks(self):
        """Load existing logic locks."""
        try:
            if os.path.exists(LOGIC_LOCKS_PATH):
                with open(LOGIC_LOCKS_PATH, 'r') as f:
                    data = json.load(f)
                    self._logic_locks = [
                        LogicLock(**lock) for lock in data.get('locks', [])
                    ]
            else:
                self._logic_locks = []
                
        except Exception as e:
            logging.error(f"Failed to load logic locks: {e}")
            self._logic_locks = []
    
    def _save_logic_locks(self):
        """Save logic locks to file."""
        try:
            data = {
                'locks': [
                    {
                        'entity_name': lock.entity_name,
                        'reason': lock.reason,
                        'future_chapter': lock.future_chapter,
                        'locked_until': lock.locked_until
                    }
                    for lock in self._logic_locks
                ],
                'updated_at': time.time()
            }
            
            with open(LOGIC_LOCKS_PATH, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Failed to save logic locks: {e}")
    
    def scan_trends(self) -> Optional[TrendContext]:
        """
        Scan external sources for trending topics.
        
        In production, this would:
        - Parse RSS feeds
        - Query trend APIs
        - Analyze social media
        - Use NLP for relevance scoring
        
        Returns:
            TrendContext if trend detected, None otherwise
        """
        logging.info("Scanning external context...")
        self._last_scan = time.time()
        
        # Mock implementation - in production, use requests + BeautifulSoup
        trending_tropes = [
            "unreliable narrators",
            "cyber-noir settings",
            "biopunk aesthetics",
            "found family dynamics",
            "morally grey protagonists",
            "time loop narratives",
            "epistolary format",
            "dual timeline structure",
            "slow burn romance",
            "cosmic horror elements"
        ]
        
        detected_trend = random.choice(trending_tropes)
        relevance_score = random.uniform(0.6, 0.95)
        
        context = TrendContext(
            trend=detected_trend,
            relevance_score=relevance_score,
            source="Literary Trends Analysis",
            timestamp=time.time()
        )
        
        # Write to context cache (File-based IPC)
        self._write_context_cache(context)
        
        logging.info(f"Context updated: {detected_trend} (relevance: {relevance_score:.2f})")
        return context
    
    def _write_context_cache(self, context: TrendContext):
        """Write context to shared cache file."""
        try:
            cache_data = {
                "timestamp": context.timestamp,
                "trending_trope": context.trend,
                "relevance_score": context.relevance_score,
                "source": context.source
            }
            
            with open(CONTEXT_CACHE_PATH, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Failed to write context cache: {e}")
    
    def read_context_cache(self) -> Optional[Dict[str, Any]]:
        """Read the current context cache."""
        try:
            if os.path.exists(CONTEXT_CACHE_PATH):
                with open(CONTEXT_CACHE_PATH, 'r') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            logging.error(f"Failed to read context cache: {e}")
            return None
    
    def add_logic_lock(self, entity_name: str, reason: str, 
                       future_chapter: str, locked_until: Optional[str] = None):
        """
        Add a logic lock to protect an entity.
        
        Used by TV Showrunner archetype to prevent killing
        characters needed for future arcs.
        
        Args:
            entity_name: Name of the protected entity
            reason: Why this entity is protected
            future_chapter: Which chapter/episode needs this entity
            locked_until: Optional date/chapter when lock expires
        """
        self._load_logic_locks()
        
        # Check if already locked
        for lock in self._logic_locks:
            if lock.entity_name.lower() == entity_name.lower():
                logging.warning(f"Entity '{entity_name}' already locked")
                return
        
        new_lock = LogicLock(
            entity_name=entity_name,
            reason=reason,
            future_chapter=future_chapter,
            locked_until=locked_until
        )
        
        self._logic_locks.append(new_lock)
        self._save_logic_locks()
        
        logging.info(f"Logic lock added: {entity_name} (until {future_chapter})")
    
    def remove_logic_lock(self, entity_name: str) -> bool:
        """Remove a logic lock."""
        self._load_logic_locks()
        
        for i, lock in enumerate(self._logic_locks):
            if lock.entity_name.lower() == entity_name.lower():
                del self._logic_locks[i]
                self._save_logic_locks()
                logging.info(f"Logic lock removed: {entity_name}")
                return True
        
        return False
    
    def check_logic_lock(self, entity_name: str) -> Optional[LogicLock]:
        """
        Check if an entity is protected by a logic lock.
        
        Args:
            entity_name: Entity to check
            
        Returns:
            LogicLock if protected, None otherwise
        """
        self._load_logic_locks()
        
        for lock in self._logic_locks:
            if lock.entity_name.lower() == entity_name.lower():
                return lock
        
        return None
    
    def check_text_for_conflicts(self, text: str) -> List[Dict[str, str]]:
        """
        Scan text for potential logic lock conflicts.
        
        Detects if the text might be trying to kill/remove
        a protected entity.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of potential conflicts
        """
        self._load_logic_locks()
        conflicts = []
        
        # Keywords that suggest entity removal
        danger_keywords = [
            "killed", "died", "death", "murdered", "assassinated",
            "destroyed", "eliminated", "removed", "vanished", "disappeared",
            "never seen again", "final breath", "last words"
        ]
        
        text_lower = text.lower()
        
        for lock in self._logic_locks:
            entity_lower = lock.entity_name.lower()
            
            if entity_lower in text_lower:
                # Check for danger keywords near entity
                for keyword in danger_keywords:
                    if keyword in text_lower:
                        # Simple proximity check
                        entity_pos = text_lower.find(entity_lower)
                        keyword_pos = text_lower.find(keyword)
                        
                        if abs(entity_pos - keyword_pos) < 100:  # Within 100 chars
                            conflicts.append({
                                "entity": lock.entity_name,
                                "keyword": keyword,
                                "reason": lock.reason,
                                "future_chapter": lock.future_chapter,
                                "warning": f"⚠️ LOGIC LOCK: Cannot remove '{lock.entity_name}' - needed for {lock.future_chapter}"
                            })
                            break
        
        return conflicts
    
    def get_all_locks(self) -> List[LogicLock]:
        """Get all current logic locks."""
        self._load_logic_locks()
        return self._logic_locks


def run_daemon(interval: int = DEFAULT_INTERVAL, sources_file: str = "rss.json"):
    """
    Run the silent listener as a background daemon.
    
    Args:
        interval: Scan interval in seconds
        sources_file: Path to sources configuration
    """
    listener = SilentListener(sources_file)
    
    logging.info(f"Silent Listener started (interval: {interval}s)")
    
    try:
        while True:
            listener.scan_trends()
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logging.info("Listener shutting down gracefully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hearth Writer Silent Listener - Background trend analysis"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Scan interval in seconds (default: {DEFAULT_INTERVAL})"
    )
    parser.add_argument(
        "--sources",
        type=str,
        default="rss.json",
        help="Path to sources configuration file"
    )
    
    args = parser.parse_args()
    run_daemon(args.interval, args.sources)
