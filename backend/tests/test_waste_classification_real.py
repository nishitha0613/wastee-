"""Tests for Real AI Waste Classification & Structured Recycling Guidance."""
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

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


def test_plastic_bottle_never_classified_as_organic_or_hazardous():
    """Verify that a real plastic bottle is identified as Plastic, NOT Organic, and NOT Hazardous."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "images"
    sample_bottle_path = fixtures_dir / "test_plastic_bottle.jpg"
    assert sample_bottle_path.exists(), "Sample bottle image fixture missing."

    # Test with generic filename to ensure visual features and model classify it, not keyword heuristics
    result = classify_waste(sample_bottle_path, original_filename="IMG_83921.jpg")

    assert result["waste_type"] != WasteType.ORGANIC.value, "Plastic bottle must NEVER be classified as Organic!"
    assert result["waste_type"] != WasteType.HAZARDOUS.value, "Plastic bottle must NEVER be classified as Hazardous!"
    assert result["waste_type"] == WasteType.PLASTIC.value, f"Expected Plastic but got {result['waste_type']}"
    assert result["confidence"] >= 0.60, f"Expected confidence >= 0.60, got {result['confidence']}"
    assert not result["is_low_confidence"], "Expected high confidence for visible plastic bottle"
    assert result.get("subtype") == "PET Plastic (#1)" or "PET" in str(result.get("subtype"))


def test_uploaded_crushed_plastic_bottle_identified_as_plastic():
    """Verify that the user's uploaded transparent plastic bottle image is correctly identified as Plastic."""
    uploads_dir = Path(__file__).parent.parent / "uploads"
    uploaded_bottle = uploads_dir / "58f999afc93a43a881b4cb784b2849f9.png"
    if uploaded_bottle.exists():
        result = classify_waste(uploaded_bottle, original_filename="photo_upload.png")
        assert result["waste_type"] == WasteType.PLASTIC.value, f"Expected Plastic but got {result['waste_type']}"
        assert result["confidence"] >= 0.60, f"Expected confidence >= 0.60, got {result['confidence']}"
        assert not result["is_low_confidence"]
        assert result.get("subtype") == "PET Plastic (#1)"


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


def test_all_waste_categories_have_specific_guidance_and_bins():
    """Verify that all waste categories have non-generic, specific recycling guidance and bin mappings."""
    expected_bin_mappings = {
        WasteType.PLASTIC.value: "Dry Waste / Plastic Recycling",
        WasteType.PAPER.value: "Paper Recycling",
        WasteType.GLASS.value: "Glass Recycling",
        WasteType.METAL.value: "Metal Recycling",
        WasteType.ORGANIC.value: "Wet Waste / Composting",
        WasteType.E_WASTE.value: "Authorized E-waste Collection",
        WasteType.HAZARDOUS.value: "Appropriate Authorized Special Collection",
        WasteType.OTHER.value: "Verification Required",
    }

    expected_category_names = {
        WasteType.PLASTIC.value: "Recyclable Waste",
        WasteType.PAPER.value: "Recyclable Waste",
        WasteType.GLASS.value: "Recyclable Waste",
        WasteType.METAL.value: "Recyclable Waste",
        WasteType.ORGANIC.value: "Organic / Compostable Waste",
        WasteType.E_WASTE.value: "Electronic Waste",
        WasteType.HAZARDOUS.value: "Hazardous Waste",
        WasteType.OTHER.value: "Unidentified / Other",
    }

    for cat_key, expected_bin in expected_bin_mappings.items():
        guidance = get_recycling_guidance(cat_key)
        assert guidance["recommended_bin"] == expected_bin, f"Bin mismatch for {cat_key}"
        assert guidance["category"] == expected_category_names[cat_key], f"Category name mismatch for {cat_key}"
        assert isinstance(guidance["primary_method"], str) and len(guidance["primary_method"]) > 10
        assert isinstance(guidance["recycling_methods"], list) and len(guidance["recycling_methods"]) >= 3
        assert isinstance(guidance["action_steps"], list) and len(guidance["action_steps"]) >= 3
        assert isinstance(guidance["precautions"], list) and len(guidance["precautions"]) >= 3
        assert isinstance(guidance["environmental_impact"], str) and len(guidance["environmental_impact"]) > 20

    # Specifically check Plastic guidance:
    plastic_guidance = get_recycling_guidance(WasteType.PLASTIC.value)
    plastic_methods = " ".join(plastic_guidance["recycling_methods"]).lower()
    assert "empty the bottle completely" in plastic_methods
    assert "rinse" in plastic_methods
    assert "resin identification code" in plastic_methods or "cap and label" in plastic_methods
    assert plastic_guidance["collection_recommended"] is False, "Plastic bottles must NOT be marked for special hazardous collection"

    # Specifically check Organic guidance:
    organic_guidance = get_recycling_guidance(WasteType.ORGANIC.value)
    organic_precautions = " ".join(organic_guidance["precautions"]).lower()
    assert "plastic" in organic_precautions
    assert "glass" in organic_precautions or "metal" in organic_precautions


def test_uncertain_object_guidance_does_not_invent_recycling():
    """Verify that uncertain/Other items state inability to identify without inventing methods."""
    uncertain_guidance = get_disposal_guidance(WasteType.OTHER.value, is_low_confidence=True)
    assert "unable to confidently identify" in uncertain_guidance["primary_method"].lower()
    assert any("verify" in m.lower() or "label" in m.lower() for m in uncertain_guidance["recycling_methods"])
    assert uncertain_guidance["recommended_bin"] == "Verification Required"
    assert uncertain_guidance["collection_recommended"] is False


def test_complete_fixture_material_streams_flow():
    """Test the complete classification flow for all standard waste streams."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "images"

    stream_tests = [
        ("test_plastic_bottle.jpg", WasteType.PLASTIC.value, "Dry Waste / Plastic Recycling"),
        ("test_glass_bottle.jpg", WasteType.GLASS.value, "Glass Recycling"),
        ("test_paper_carton.jpg", WasteType.PAPER.value, "Paper Recycling"),
        ("test_food_organic.jpg", WasteType.ORGANIC.value, "Wet Waste / Composting"),
        ("test_metal_can.jpg", WasteType.METAL.value, "Metal Recycling"),
        ("test_ewaste_keyboard.jpg", WasteType.E_WASTE.value, "Authorized E-waste Collection"),
        ("test_hazardous_battery.jpg", WasteType.HAZARDOUS.value, "Appropriate Authorized Special Collection"),
    ]

    for fname, expected_type, expected_bin in stream_tests:
        fpath = fixtures_dir / fname
        assert fpath.exists(), f"Fixture missing: {fname}"

        res = classify_waste(fpath, original_filename="test_upload.jpg")
        assert res["waste_type"] == expected_type, f"Expected {expected_type} for {fname}, got {res['waste_type']}"
        assert res["confidence"] >= 0.60, f"Expected confidence >= 0.60 for {fname}, got {res['confidence']}"
        assert not res["is_low_confidence"]

        guidance = get_disposal_guidance(res["waste_type"], subtype=res.get("subtype"))
        assert guidance["recommended_bin"] == expected_bin


def test_blank_solid_unidentifiable_image_categorized_as_other():
    """Verify that a blank or featureless image is categorized as Other with low confidence."""
    import tempfile
    img = Image.new("RGB", (224, 224), color=(200, 200, 200))
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        img.save(tmp.name)
        tmp_path = Path(tmp.name)

    try:
        res = classify_waste(tmp_path, original_filename="blank.jpg")
        assert res["waste_type"] == WasteType.OTHER.value
        assert res["is_low_confidence"] is True
        assert res["confidence"] < 0.60

        guidance = get_disposal_guidance(res["waste_type"], is_low_confidence=True)
        assert guidance["recommended_bin"] == "Verification Required"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
