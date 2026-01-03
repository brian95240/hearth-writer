"""
Hearth Writer Core Module
=========================
The Logic Core of Hearth Writer v1.2 "Vertex"

Modules:
- context_engine: RAG, Shadow Nodes, Visual State tracking
- inference_process: Isolated multiprocessing AI worker
- license_validator: Defense in Depth licensing
- pure_mode: Voice baseline and drift detection
- resource_manager: Collapse-to-Zero orchestration
- silent_listener: Background trend analysis
- voice_engine: TTS/ASR with LRU caching

Usage:
    from core import ResourceOrchestrator, LicenseValidator
    from core.context_engine import SeriesContextEngine
"""

from .license_validator import (
    LicenseValidator,
    get_validator,
    get_license_tier,
    check_feature_access,
    can_access_feature,
    LicenseTier,
)

from .resource_manager import (
    ResourceOrchestrator,
    orchestrator,
    ModelState,
)

from .inference_process import InferenceWorker

__all__ = [
    # License
    'LicenseValidator',
    'get_validator',
    'get_license_tier',
    'check_feature_access',
    'can_access_feature',
    'LicenseTier',
    
    # Resource Management
    'ResourceOrchestrator',
    'orchestrator',
    'ModelState',
    
    # Inference
    'InferenceWorker',
]

__version__ = "1.2.0"
__codename__ = "Vertex"
