"""
Hearth Writer License Validator
================================
Centralized licensing logic for Defense in Depth architecture.

This module provides a single source of truth for license validation,
ensuring consistent enforcement across all core modules.

License Tiers:
- RONIN (Free): Basic prose/screenplay, linear timeline, single model
- ARCHITECT ($19/mo): Shadow Nodes, Visual Tracking, Multi-LORA, Timeline Injection
- SHOWRUNNER ($49/seat): All Architect features + Team Sync, White Labeling, Legal Indemnity

Usage:
    from core.license_validator import LicenseValidator
    
    validator = LicenseValidator()
    if validator.can_access("shadow_nodes"):
        # Execute pro feature
    else:
        # Return locked message
"""

import os
import hashlib
import logging
from typing import Tuple, Dict, List
from dataclasses import dataclass
from enum import Enum

class LicenseTier(Enum):
    RONIN = "ronin"
    ARCHITECT = "architect"
    SHOWRUNNER = "showrunner"

@dataclass
class FeatureAccess:
    allowed: bool
    tier_required: str
    message: str

# Feature to Tier mapping
FEATURE_TIERS: Dict[str, List[LicenseTier]] = {
    # Architect+ Features
    "shadow_nodes": [LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    "visual_tracking": [LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    "multi_lora": [LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    "timeline_injection": [LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    "comic_mode": [LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    
    # Showrunner-Only Features
    "collaboration": [LicenseTier.SHOWRUNNER],
    "team_sync": [LicenseTier.SHOWRUNNER],
    "white_labeling": [LicenseTier.SHOWRUNNER],
    "custom_grammars": [LicenseTier.SHOWRUNNER],
    
    # Free Features (all tiers)
    "prose_mode": [LicenseTier.RONIN, LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    "screenplay_mode": [LicenseTier.RONIN, LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    "voice_engine": [LicenseTier.RONIN, LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
    "pure_mode": [LicenseTier.RONIN, LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER],
}

# User-friendly denial messages
DENIAL_MESSAGES: Dict[str, str] = {
    "shadow_nodes": "⚠️ FEATURE LOCKED: Shadow Nodes & Timeline Injection require the 'Architect' License.",
    "visual_tracking": "⚠️ FEATURE LOCKED: Visual Tagging requires the 'Architect' License.",
    "multi_lora": "⚠️ FEATURE LOCKED: Multi-LORA Mixing requires the 'Architect' License.",
    "timeline_injection": "⚠️ FEATURE LOCKED: Timeline Injection requires the 'Architect' License.",
    "comic_mode": "⚠️ FEATURE LOCKED: Comic/Marvel Mode requires the 'Architect' License.",
    "collaboration": "⚠️ FEATURE LOCKED: Team Sync requires the 'Showrunner' License.",
    "team_sync": "⚠️ FEATURE LOCKED: Team Sync requires the 'Showrunner' License.",
    "white_labeling": "⚠️ FEATURE LOCKED: White Labeling requires the 'Showrunner' License.",
    "custom_grammars": "⚠️ FEATURE LOCKED: Custom Grammar Files require the 'Showrunner' License.",
}


class LicenseValidator:
    """
    Centralized license validation for Hearth Writer.
    
    Implements Defense in Depth: Even if one layer is bypassed,
    each core module independently validates license status.
    """
    
    # Valid key prefixes for each tier
    KEY_PREFIXES = {
        "HRTH_ARCHITECT_": LicenseTier.ARCHITECT,
        "HRTH_SHOWRUNNER_": LicenseTier.SHOWRUNNER,
    }
    
    def __init__(self):
        self._cached_tier = None
        self._key_hash = None
        
    def _get_key(self) -> str:
        """Retrieve license key from environment."""
        return os.environ.get("HEARTH_LICENSE_KEY", "")
    
    def _validate_key_format(self, key: str) -> Tuple[bool, LicenseTier]:
        """
        Validates key format and returns tier.
        
        In v1.2, this is a simple prefix check.
        In v2.0+, this would hit a validation server.
        """
        if not key:
            return False, LicenseTier.RONIN
        
        for prefix, tier in self.KEY_PREFIXES.items():
            if key.startswith(prefix):
                return True, tier
        
        return False, LicenseTier.RONIN
    
    def get_tier(self) -> LicenseTier:
        """
        Returns the current license tier.
        Caches result to avoid repeated env lookups.
        """
        key = self._get_key()
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        
        # Return cached if key hasn't changed
        if self._key_hash == key_hash and self._cached_tier is not None:
            return self._cached_tier
        
        # Validate and cache
        is_valid, tier = self._validate_key_format(key)
        self._cached_tier = tier
        self._key_hash = key_hash
        
        logging.info(f"License tier resolved: {tier.value.upper()}")
        return tier
    
    def get_tier_name(self) -> str:
        """Returns the tier name as a string."""
        return self.get_tier().value
    
    def can_access(self, feature_name: str) -> bool:
        """
        Quick check if current tier can access a feature.
        
        Args:
            feature_name: The feature to check (e.g., "shadow_nodes")
            
        Returns:
            True if access is allowed, False otherwise
        """
        current_tier = self.get_tier()
        allowed_tiers = FEATURE_TIERS.get(feature_name, [])
        
        # If feature not in map, default allow (future-proofing)
        if not allowed_tiers:
            return True
        
        return current_tier in allowed_tiers
    
    def check_access(self, feature_name: str) -> FeatureAccess:
        """
        Full access check with detailed response.
        
        Args:
            feature_name: The feature to check
            
        Returns:
            FeatureAccess dataclass with allowed status and message
        """
        current_tier = self.get_tier()
        allowed_tiers = FEATURE_TIERS.get(feature_name, [])
        
        if not allowed_tiers or current_tier in allowed_tiers:
            return FeatureAccess(
                allowed=True,
                tier_required=current_tier.value,
                message="Access Granted"
            )
        
        # Determine minimum required tier
        if LicenseTier.ARCHITECT in allowed_tiers:
            tier_required = "architect"
        else:
            tier_required = "showrunner"
        
        return FeatureAccess(
            allowed=False,
            tier_required=tier_required,
            message=DENIAL_MESSAGES.get(feature_name, f"⚠️ FEATURE LOCKED: {feature_name} requires upgrade.")
        )
    
    def is_pro(self) -> bool:
        """Returns True if user has any paid tier."""
        return self.get_tier() in [LicenseTier.ARCHITECT, LicenseTier.SHOWRUNNER]
    
    def is_enterprise(self) -> bool:
        """Returns True if user has Showrunner tier."""
        return self.get_tier() == LicenseTier.SHOWRUNNER
    
    def get_unlocked_features(self) -> List[str]:
        """Returns list of all features available to current tier."""
        current_tier = self.get_tier()
        return [
            feature for feature, tiers in FEATURE_TIERS.items()
            if current_tier in tiers
        ]
    
    def get_locked_features(self) -> List[str]:
        """Returns list of features locked for current tier."""
        current_tier = self.get_tier()
        return [
            feature for feature, tiers in FEATURE_TIERS.items()
            if current_tier not in tiers
        ]


# Singleton instance for convenience
_validator_instance = None

def get_validator() -> LicenseValidator:
    """Returns singleton LicenseValidator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = LicenseValidator()
    return _validator_instance


# Convenience functions for direct import
def get_license_tier() -> str:
    """Returns current license tier as string."""
    return get_validator().get_tier_name()

def check_feature_access(feature_name: str) -> Tuple[bool, str]:
    """
    Returns (Allowed: bool, Message: str) for compatibility with app.py
    """
    access = get_validator().check_access(feature_name)
    return access.allowed, access.message

def can_access_feature(feature_name: str) -> bool:
    """Quick boolean check for feature access."""
    return get_validator().can_access(feature_name)
