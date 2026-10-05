#!/usr/bin/env python3
"""
Test all 8 waste categories for disposal guidance completeness:
  - Organic
  - Plastic
  - Paper
  - Glass
  - Metal
  - E-Waste
  - Hazardous
  - Other
Verifying:
  1. Disposal / Recycling Recommendation
  2. Recommended Action Steps (>= 3 practical steps)
  3. Important Precautions (>= 3 practical items)
  4. Environmental Impact
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.disposal_guidance import get_disposal_guidance
from app.models.waste_report import WasteType

def verify_category_guidance(category_name, expected_kw):
    guidance = get_disposal_guidance(category_name)
    assert guidance is not None, f"No guidance returned for {category_name}"

    rec = guidance.get("recommendation") or guidance.get("disposal_method")
    steps = guidance.get("action_steps") or guidance.get("do")
    precautions = guidance.get("precautions") or guidance.get("dont")
    impact = guidance.get("environmental_impact")

    print(f"\n=================== CATEGORY: {category_name} ===================")
    print(f"Recommendation: {rec}")
    print(f"Action Steps ({len(steps)}):")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    print(f"Precautions ({len(precautions)}):")
    for i, p in enumerate(precautions, 1):
        print(f"  {i}. {p}")
    print(f"Environmental Impact: {impact}")

    # Assertions
    assert rec and len(rec) > 15, f"Recommendation too short for {category_name}"
    assert len(steps) >= 3, f"Expected at least 3 action steps for {category_name}, got {len(steps)}"
    assert len(precautions) >= 3, f"Expected at least 3 precautions for {category_name}, got {len(precautions)}"
    assert impact and len(impact) > 20, f"Environmental impact missing or short for {category_name}"
    assert expected_kw.lower() in rec.lower() or expected_kw.lower() in str(steps).lower(), f"Keyword {expected_kw} missing in {category_name}"

def main():
    test_cases = [
        ("Organic", "compost"),
        ("Plastic", "recycl"),
        ("Paper", "paper"),
        ("Glass", "glass"),
        ("Metal", "metal"),
        ("E-Waste", "e-waste"),
        ("Hazardous", "hazardous"),
        ("Other", "label"),
    ]

    for cat, kw in test_cases:
        verify_category_guidance(cat, kw)

    print("\n-------------------------------------------------------------")
    print("ALL 8 CATEGORIES FULLY VERIFIED WITH ACTION STEPS & PRECAUTIONS")
    print("-------------------------------------------------------------")

if __name__ == "__main__":
    main()
