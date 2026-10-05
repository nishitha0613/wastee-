"""Disposal Guidance Service.

Provides structured, actionable disposal guidance based on identified waste categories.
Integrates with the dedicated Recycling Guidance Service (app.services.recycling_guidance).
"""
from typing import Dict, Any, List
from app.models.waste_report import WasteType
from app.services.recycling_guidance import (
    RECYCLING_GUIDANCE_CATALOG,
    get_recycling_guidance,
)


def _build_guidance_database() -> Dict[str, Dict[str, Any]]:
    """Builds the comprehensive guidance database combining recycling and disposal information."""
    db: Dict[str, Dict[str, Any]] = {}
    for cat_name, info in RECYCLING_GUIDANCE_CATALOG.items():
        entry = info.copy()
        # Keep backward-compatible keys
        entry["disposal_method"] = info.get("primary_method", "")
        entry["recommendation"] = info.get("primary_method", "")
        entry["do"] = info.get("action_steps", [])
        entry["dont"] = info.get("precautions", [])
        db[cat_name] = entry
    return db


GUIDANCE_DATABASE: Dict[str, Dict[str, Any]] = _build_guidance_database()


def get_disposal_guidance(waste_type: str, is_low_confidence: bool = False) -> Dict[str, Any]:
    """Retrieve structured disposal guidance and recycling methods for a given waste type.

    Returns category, primary_method, recycling_methods, disposal_method, recommendation,
    actionable dos/action_steps, precautions/donts, environmental impact,
    recyclability indicator, and collection recommendation.
    """
    raw_guidance = get_recycling_guidance(waste_type, is_low_confidence=is_low_confidence)
    result = raw_guidance.copy()
    result["disposal_method"] = raw_guidance.get("primary_method", "")
    result["recommendation"] = raw_guidance.get("primary_method", "")
    result["do"] = raw_guidance.get("action_steps", [])
    result["dont"] = raw_guidance.get("precautions", [])
    return result
