"""Tests for Real AI Waste Classification & Structured Recycling Guidance."""
import pytest
from pathlib import Path
from app.services.waste_classifier import (
    classify_waste,
    get_waste_classifier,
    ONNXWasteClassifier,
)
from app.services.recycling_guidance import (
    get_recycling_guidance,
    RECYCLING_GUIDANCE_CATALOG,
)
from app.services.disposal_guidance import get_disposal_guidance
from app.models.waste_report import WasteType


def test_plastic_bottle_never_classified_as_organic():
    """Verify that a real plastic bottle is identified as Plastic and NEVER Organic."""
    sample_bottle_path = Path(__file__).parent.parent.parent / "public" / "sample-bottle.jpg"
    assert sample_bottle_path.exists(), "Sample bottle image fixture missing."

    # Test with generic filename to ensure visual features and model classify it, not keyword heuristics
    result = classify_waste(sample_bottle_path, original_filename="IMG_83921.jpg")

    assert result["waste_type"] != WasteType.ORGANIC.value, "Plastic bottle must NEVER be classified as Organic!"
    assert result["waste_type"] == WasteType.PLASTIC.value, f"Expected Plastic but got {result['waste_type']}"
    assert result["confidence"] >= 0.60, f"Expected confidence >= 0.60, got {result['confidence']}"
    assert not result["is_low_confidence"], "Expected high confidence for visible plastic bottle"
    assert "water bottle" in result.get("raw_class_name", "").lower() or "bottle" in result.get("raw_class_name", "").lower()


def test_confidence_threshold_below_cutoff():
    """Verify that predictions below AI_CONFIDENCE_THRESHOLD (0.60) map to 'Other' with warning."""
    classifier = get_waste_classifier()
    raw_mock = {
        "waste_type": WasteType.PLASTIC.value,
        "confidence": 0.45,
        "raw_class_name": "ambiguous_object",
        "model_used": "TestModel",
    }
    evaluated = classifier.apply_confidence_threshold(raw_mock, threshold=0.60)

    assert evaluated["waste_type"] == WasteType.OTHER.value
    assert evaluated["is_low_confidence"] is True
    assert evaluated["confidence"] == 0.45
    assert "Identification uncertain" in evaluated["message"]


def test_all_waste_categories_have_specific_recycling_methods():
    """Verify that all waste categories have non-generic, specific recycling guidance."""
    expected_categories = [
        WasteType.ORGANIC.value,
        WasteType.PLASTIC.value,
        WasteType.PAPER.value,
        WasteType.GLASS.value,
        WasteType.METAL.value,
        WasteType.E_WASTE.value,
        WasteType.HAZARDOUS.value,
        WasteType.OTHER.value,
    ]

    for cat in expected_categories:
        guidance = get_recycling_guidance(cat)
        assert guidance["category"] == cat
        assert isinstance(guidance["primary_method"], str) and len(guidance["primary_method"]) > 10
        assert isinstance(guidance["recycling_methods"], list) and len(guidance["recycling_methods"]) >= 3
        assert isinstance(guidance["action_steps"], list) and len(guidance["action_steps"]) >= 3
        assert isinstance(guidance["precautions"], list) and len(guidance["precautions"]) >= 3
        assert isinstance(guidance["environmental_impact"], str) and len(guidance["environmental_impact"]) > 20

    # Specifically check Plastic recycling steps mention emptying, rinsing, and not claiming all is recyclable
    plastic_guidance = get_recycling_guidance(WasteType.PLASTIC.value)
    plastic_text = " ".join(plastic_guidance["recycling_methods"] + plastic_guidance["action_steps"]).lower()
    assert "rinse" in plastic_text or "empty" in plastic_text
    assert "recycling symbol" in plastic_text or "resin" in plastic_text

    # Specifically check Organic steps mention composting and not mixing plastic/glass/metal
    organic_guidance = get_recycling_guidance(WasteType.ORGANIC.value)
    organic_precautions = " ".join(organic_guidance["precautions"]).lower()
    assert "plastic" in organic_precautions
    assert "glass" in organic_precautions or "metal" in organic_precautions


def test_uncertain_object_guidance_does_not_invent_recycling():
    """Verify that uncertain/Other items state inability to identify without inventing methods."""
    uncertain_guidance = get_disposal_guidance(WasteType.OTHER.value, is_low_confidence=True)
    assert "unable to confidently identify" in uncertain_guidance["primary_method"].lower()
    assert any("verify" in m.lower() or "label" in m.lower() for m in uncertain_guidance["recycling_methods"])
