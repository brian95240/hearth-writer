import numpy as np
import logging
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
# Assuming generic local vector store (e.g., LanceDB or FAISS-lite)
import lancedb 

# Import the previously defined Orchestrator
from core.resource_manager import ResourceOrchestrator

@dataclass
class RetrievalResult:
    content: str
    metadata: Dict[str, str]
    score: float

# --- LICENSE VALIDATION (Defense in Depth) ---
def get_license_tier():
    """
    Checks for a valid license key in the environment.
    Mirrors the check in app.py for defense in depth.
    """
    key = os.environ.get("HEARTH_LICENSE_KEY", "")
    if not key:
        return "ronin"
    if key.startswith("HRTH_ARCHITECT_"):
        return "architect"
    if key.startswith("HRTH_SHOWRUNNER_"):
        return "showrunner"
    return "ronin"

def check_pro_feature(feature_name: str) -> bool:
    """
    Returns True if the current license allows access to the feature.
    Defense in Depth: Even if app.py is bypassed, core engine refuses pro features.
    """
    tier = get_license_tier()
    
    if feature_name in ["shadow_nodes", "visual_tracking", "multi_lora"]:
        return tier in ["architect", "showrunner"]
    
    if feature_name == "collaboration":
        return tier == "showrunner"
    
    return True  # Default allow for unlocked features


class SeriesContextEngine:
    """
    Manages the 'Series Planner' and 'World Bible'.
    Operates on a 'Pulse' basis: Wake -> Retrieve -> Sleep.
    """
    
    def __init__(self, orchestrator: ResourceOrchestrator, db_path: str):
        self.orchestrator = orchestrator
        self.db_path = db_path
        self._db_connection = None # Lazy connection
        
    @property
    def db(self):
        """Lazy load the database connection."""
        if self._db_connection is None:
            self._db_connection = lancedb.connect(self.db_path)
        return self._db_connection

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Micro-Transaction:
        1. Request Embedding Model (Warm Circuit check).
        2. Compute Vector.
        3. Release Lock immediately.
        """
        # 1. Request Resource
        embedder = self.orchestrator.request_model("all-MiniLM-L6-v2", keep_warm=False)
        
        # 2. Compute (Mocking the inference call)
        # vector = embedder.encode(text) 
        vector = np.random.rand(384) # 384-dim vector mock
        
        # 3. Release Lock (Signal Orchestrator this resource is free to be purged)
        self.orchestrator.release_lock("all-MiniLM-L6-v2")
        
        return vector

    def retrieve_shadow_nodes(self, query: str, limit: int = 5) -> List[RetrievalResult]:
        """
        Retrieves Shadow Nodes (Open Loops, Timeline Branches) from the series database.
        
        HARD LOCK: This is a PRO feature. Returns empty if not licensed.
        Defense in Depth layer - even if app.py intent router is bypassed,
        the core engine still refuses to serve pro features.
        """
        # HARD LOCK - Defense in Depth
        if not check_pro_feature("shadow_nodes"):
            logging.warning("Shadow Nodes access denied - Ronin tier detected")
            return []  # Return nothing if not Pro
        
        # Vectorize Query
        query_vector = self._get_embedding(query)
        
        # Search Shadow Nodes table
        try:
            tbl = self.db.open_table("shadow_nodes")
            results = tbl.search(query_vector).limit(limit).to_list()
            
            shadow_hits = []
            for r in results:
                shadow_hits.append(RetrievalResult(
                    content=r['text'],
                    metadata={
                        'type': 'shadow_node',
                        'timeline': r.get('timeline', 'main'),
                        'status': r.get('status', 'open'),
                        'chapter_ref': r.get('chapter_ref', 'unknown')
                    },
                    score=1 - r.get('_distance', 0.5)
                ))
            
            logging.info(f"Retrieved {len(shadow_hits)} shadow nodes for query")
            return shadow_hits
            
        except Exception as e:
            logging.error(f"Shadow Node retrieval error: {e}")
            return []

    def retrieve_visual_state(self, entity: str) -> Dict[str, str]:
        """
        Retrieves Visual State metadata for comic/visual continuity.
        
        HARD LOCK: This is a PRO feature (Visual Tracking).
        """
        # HARD LOCK - Defense in Depth
        if not check_pro_feature("visual_tracking"):
            logging.warning("Visual Tracking access denied - Ronin tier detected")
            return {}  # Return nothing if not Pro
        
        try:
            tbl = self.db.open_table("visual_states")
            # Query by entity name
            results = tbl.search(entity).limit(1).to_list()
            
            if results:
                return {
                    'entity': entity,
                    'costume_state': results[0].get('costume_state', 'default'),
                    'damage_state': results[0].get('damage_state', 'none'),
                    'location': results[0].get('location', 'unknown'),
                    'last_panel': results[0].get('last_panel', '0'),
                    'visual_notes': results[0].get('visual_notes', '')
                }
            return {}
            
        except Exception as e:
            logging.error(f"Visual State retrieval error: {e}")
            return {}

    def retrieve_context(self, query: str, limit: int = 3, threshold: float = 0.75) -> List[RetrievalResult]:
        """
        Executes the Retrieval step for general context (available to all tiers).
        """
        # 1. Vectorize Query (Transient Model Load)
        query_vector = self._get_embedding(query)
        
        # 2. Disk-based Vector Search (No massive index in RAM)
        tbl = self.db.open_table("series_bible")
        results = tbl.search(query_vector).limit(limit).to_list()
        
        # 3. Filter & Format
        context_hits = []
        for r in results:
            if r['_distance'] < (1 - threshold): # Assuming cosine distance
                context_hits.append(RetrievalResult(
                    content=r['text'],
                    metadata=r['metadata'],
                    score=1 - r['_distance']
                ))
                
        return context_hits

    def generate_with_context(self, prompt: str, context_hits: List[RetrievalResult], 
                              include_shadows: bool = False, include_visuals: bool = False):
        """
        The Synthesis Step.
        
        Args:
            prompt: User's input text
            context_hits: Retrieved context from series bible
            include_shadows: Whether to include Shadow Nodes (license checked)
            include_visuals: Whether to include Visual State (license checked)
        """
        # 1. Construct Augmented Prompt
        context_block = "\n".join([f"[{r.metadata.get('type', 'context')}]: {r.content}" for r in context_hits])
        
        # 2. Optionally inject Shadow Nodes (Pro feature - will return empty if not licensed)
        shadow_block = ""
        if include_shadows:
            shadow_hits = self.retrieve_shadow_nodes(prompt)
            if shadow_hits:
                shadow_block = "\n[SHADOW NODES - OPEN LOOPS]:\n" + "\n".join([
                    f"  - {s.content} (Timeline: {s.metadata['timeline']}, Status: {s.metadata['status']})"
                    for s in shadow_hits
                ])
        
        # 3. Optionally inject Visual State (Pro feature - will return empty if not licensed)
        visual_block = ""
        if include_visuals:
            # Extract entity names from prompt (simplified)
            import re
            entities = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            for entity in entities[:3]:  # Limit to first 3 proper nouns
                visual_state = self.retrieve_visual_state(entity)
                if visual_state:
                    visual_block += f"\n[VISUAL STATE - {entity}]: {visual_state}"
        
        augmented_prompt = f"CONTEXT:\n{context_block}{shadow_block}{visual_block}\n\nSTORY:\n{prompt}"
        
        # 4. Request Generation Model (Heavier Resource)
        # We hold the lock here because generation takes time (Seconds vs Milliseconds)
        llm = self.orchestrator.request_model("mistral-7b-quantized", keep_warm=True)
        
        # 5. Generate (Stream output to UI)
        # output = llm.generate(augmented_prompt, stream=True)...
        logging.info(f"Generating with augmented prompt ({len(augmented_prompt)} chars)")
        
        # 6. Release Lock upon completion
        self.orchestrator.release_lock("mistral-7b-quantized")
        
        # 7. Trigger Cleanup (Optional: immediate GC if user pauses)
        # self.orchestrator.collapse_to_zero()
        
        return augmented_prompt  # Return for debugging; actual impl returns generated text


# --- Workflow Integration ---

# Initialize (lazy - actual connection happens on first use)
# orchestrator must be imported from resource_manager
try:
    from core.resource_manager import orchestrator
    rag_engine = SeriesContextEngine(orchestrator, "./data/series_db")
except ImportError:
    # Fallback for standalone testing
    rag_engine = None
    logging.warning("RAG Engine not initialized - orchestrator not available")

# Example Usage (when running as module):
# User types: "Brian enters the secret lab."
# Trigger: Detect entity "Brian" or location "secret lab"
# query = "Brian secret lab specifications"
#
# 1. Retrieve (Fast, low memory spike)
# hits = rag_engine.retrieve_context(query)
#
# 2. Generate with Shadow Nodes (High memory spike, sustained)
# The system automatically loads the LLM *after* the Embedder is released.
# This ensures we don't have (Embedding Model + LLM) in VRAM simultaneously.
# rag_engine.generate_with_context("Brian enters the secret lab.", hits, include_shadows=True)
