"""Dedicated Recycling Guidance Service.

Provides structured, category-specific recycling methods, action steps, precautions,
and environmental impact assessments.

Adheres strictly to waste material streams:
- Organic (composting, wet waste collection, do NOT mix plastic/metal/glass)
- Plastic (identification of resin codes, rinsing, certified recycling points, do NOT claim all is recyclable)
- Paper (clean dry paper/cardboard recycling, contaminants removal, soiled paper caveats)
- Glass (color sorting, rinsing, dedicated drop-off, safely wrap broken glass)
- Metal (can/scrap separation, rinsing, scrap metal recovery, safe aerosol handling)
- E-Waste (authorized WEEE collection, manufacturer take-back, battery separation)
- Hazardous (licensed toxic management, safe original storage, no household bin disposal)
- Other / Unknown (unidentified item verification, label checking, administrator collection assistance)
"""
from typing import Dict, Any, List
from app.models.waste_report import WasteType


RECYCLING_GUIDANCE_CATALOG: Dict[str, Dict[str, Any]] = {
    WasteType.ORGANIC.value: {
        "category": WasteType.ORGANIC.value,
        "primary_method": "Home composting and municipal wet-waste collection",
        "recycling_methods": [
            "Home composting: Set up an aerated compost bin or heap for raw kitchen scraps and organic yard trimmings.",
            "Municipal wet-waste / green-bin collection: Deposit segregated biodegradables into designated local green bins.",
            "Community composting: Deliver bulk food scraps to neighborhood community composting facilities where available."
        ],
        "action_steps": [
            "Separate food and kitchen waste (vegetable peels, fruit rinds, leftover food, coffee grounds) from dry recyclables.",
            "Put it into an appropriate composting or wet-waste system.",
            "Maintain suitable moisture and aeration to promote active aerobic decomposition."
        ],
        "precautions": [
            "Do not mix plastic wrappers, stickers, carry bags, or packaging with organic waste.",
            "Do not mix glass, metal cans, or ceramic dishware into composting streams.",
            "Do not include non-biodegradable packaging, treated lumber, or hazardous chemicals."
        ],
        "environmental_impact": "Composting organic matter cuts municipal landfill methane emissions, enriches topsoil with essential nutrients, and eliminates synthetic fertilizer demand.",
        "recyclable": True,
        "collection_recommended": False,
    },
    WasteType.PLASTIC.value: {
        "category": WasteType.PLASTIC.value,
        "primary_method": "Plastic segregation and certified mechanical recycling",
        "recycling_methods": [
            "Identify the plastic type and recycling symbol (e.g. PET #1, HDPE #2, PP #5) on the bottom or label where possible.",
            "Empty and rinse recyclable containers thoroughly to remove food grease, sugar, and beverage residues.",
            "Separate recyclable rigid plastic from contaminated, degraded, or multi-layer metallized wrappers.",
            "Take suitable clean plastic to a municipal recycling collection point or authorized plastic recycling partner."
        ],
        "action_steps": [
            "Empty the bottle or container completely before disposal.",
            "Rinse it if necessary to prevent souring and pest attraction.",
            "Keep the bottle separate from wet and organic waste.",
            "Put it in the appropriate dry/recyclable waste stream or authorized plastic collection point.",
            "Keep caps and labels handled according to local recycling instructions (e.g., flatten bottle and re-secure cap if accepted locally)."
        ],
        "precautions": [
            "Do not claim or assume every type of plastic is recyclable; check local facility capabilities and resin codes.",
            "Never burn plastic waste, as it releases toxic dioxins, furans, and hazardous atmospheric pollutants.",
            "Avoid mixing heavily soiled, motor-oil-contaminated, or chemical-coated plastics with clean recyclables."
        ],
        "environmental_impact": "Recycling plastic conserves finite petroleum reserves, prevents plastic leakage into marine and river ecosystems, and cuts carbon emissions by up to 70% compared to virgin plastic manufacturing.",
        "recyclable": True,
        "collection_recommended": False,
    },
    WasteType.PAPER.value: {
        "category": WasteType.PAPER.value,
        "primary_method": "Clean paper and cardboard repulping and recycling",
        "recycling_methods": [
            "Paper recycling: Bundle dry newspapers, office sheets, notebooks, envelopes, and paper packaging.",
            "Cardboard recycling: Flatten corrugated shipping boxes, cereal cartons, and paperboard sleeves to optimize space.",
            "Separation of clean/dry paper: Keep materials sheltered from rain and moisture to retain fiber tensile strength.",
            "Contamination removal: Strip plastic adhesive tape, bubble padding, metal binder clips, and plastic sleeves."
        ],
        "action_steps": [
            "Keep paper and cardboard completely clean and dry before recycling.",
            "Separate cardboard shipping boxes from fine paper and flatten them securely.",
            "Remove obvious non-paper contamination such as packaging tape, heavy staples, and plastic lamination."
        ],
        "precautions": [
            "Wet or food-contaminated paper (such as grease-soaked pizza boxes or used paper napkins) is not suitable for paper recycling; compost or place in residual waste.",
            "Do not place thermal cash register receipts, wax-coated cartons, or plastic-laminated foils in paper recycling bins.",
            "Avoid putting paper soiled with automotive lubricants, paints, or chemicals into recycling streams."
        ],
        "environmental_impact": "Recycling each ton of paper saves approximately 17 mature trees, 26,000 liters of fresh water, and avoids substantial landfill methane generation.",
        "recyclable": True,
        "collection_recommended": False,
    },
    WasteType.GLASS.value: {
        "category": WasteType.GLASS.value,
        "primary_method": "Closed-loop circular glass container recycling",
        "recycling_methods": [
            "Separate glass containers (bottles, jars, flacons) from household trash and sort by color (clear, amber, green) where requested.",
            "Rinse glass containers cleanly when appropriate to dislodge remaining sauces, syrups, and liquids.",
            "Take sorted intact containers to dedicated municipal glass-recycling banks or drop-off igloos.",
            "Safely handle broken glass by wrapping it securely in puncture-proof material before disposal."
        ],
        "action_steps": [
            "Separate glass containers from general waste and rinse cleanly.",
            "Remove non-glass closures such as plastic pourers, cork stoppers, and metal caps before drop-off.",
            "Safely deliver intact containers to a designated municipal glass drop-off point or neighborhood bottle bank."
        ],
        "precautions": [
            "Never place loose broken glass into collection bags where it could injure collection workers; wrap securely in stiff cardboard or thick paper.",
            "Do not mix window panes, mirrors, Pyrex glassware, laboratory vials, light bulbs, or ceramics with container glass (they have different melting temperatures).",
            "Do not leave sealed glass containers filled with fermenting or carbonated liquids in collection bins."
        ],
        "environmental_impact": "Glass is 100% recyclable indefinitely with zero loss in purity or strength. Substituting cullet into glass furnaces significantly lowers melting temperatures and greenhouse gas emissions.",
        "recyclable": True,
        "collection_recommended": False,
    },
    WasteType.METAL.value: {
        "category": WasteType.METAL.value,
        "primary_method": "Scrap metal recovery and secondary smelting",
        "recycling_methods": [
            "Separate metal containers (aluminum beverage cans, tin-plated food cans) from general refuse.",
            "Clean and rinse food tins where appropriate to eliminate organic remnants and odor.",
            "Send sorted metals to municipal dry-recycling bins or certified scrap-metal buy-back centers.",
            "Recover valuable non-ferrous and ferrous metals rather than letting them rust or occupy landfill volume."
        ],
        "action_steps": [
            "Separate metal cans and clean scrap items from mixed garbage.",
            "Rinse food tins thoroughly and allow them to drain dry.",
            "Deposit into the municipal metal recycling stream or hand over to an authorized scrap recycler."
        ],
        "precautions": [
            "Do not crush or puncture aerosol cans unless they are completely empty and depressurized.",
            "Never place pressurized gas canisters, fire extinguishers, or pesticide containers into standard recycling bins.",
            "Avoid mixing scrap metal contaminated with wet paint, motor lubricants, or corrosive chemicals with clean cans."
        ],
        "environmental_impact": "Recycling aluminum requires 95% less energy than extracting it from virgin bauxite ore, drastically reducing mining deforestation and toxic tailings.",
        "recyclable": True,
        "collection_recommended": False,
    },
    WasteType.E_WASTE.value: {
        "category": WasteType.E_WASTE.value,
        "primary_method": "Authorized WEEE facility dismantling and precious metal recovery",
        "recycling_methods": [
            "Deliver electronics to authorized e-waste collection centers or municipal e-waste drop-off drives.",
            "Take advantage of manufacturer and retailer take-back or trade-in programs where available.",
            "Separate detachable lithium-ion/alkaline batteries, charging cables, and accessories for targeted handling.",
            "Ensure certified responsible recycling that reclaims precious metals and neutralizes toxic components."
        ],
        "action_steps": [
            "Take electronic devices, household appliances, and computing accessories directly to an authorized e-waste collector.",
            "Remove and isolate detachable batteries, memory cards, and power cords before drop-off.",
            "Perform factory reset and wipe personal data from memory storage on smart devices prior to recycling."
        ],
        "precautions": [
            "Do NOT recommend or place e-waste in normal household garbage or single-stream recycling bins.",
            "Do not attempt to dismantle screens, CRTs, or battery casings at home, as they contain hazardous mercury, lead, and acid electrolytes.",
            "Never burn electrical cables to extract copper; the open combustion produces carcinogenic dioxins."
        ],
        "environmental_impact": "Formal e-waste recycling reclaims strategic rare-earth elements, gold, silver, and copper while preventing heavy metals (cadmium, lead, mercury) from contaminating drinking water tables.",
        "recyclable": True,
        "collection_recommended": True,
    },
    WasteType.HAZARDOUS.value: {
        "category": WasteType.HAZARDOUS.value,
        "primary_method": "Authorized hazardous-waste facility containment and neutralization",
        "recycling_methods": [
            "Transport to authorized hazardous-waste handling facilities or designated municipal toxic drop-off days.",
            "Practice safe handling by retaining chemicals in original, clearly labeled containers with closed caps.",
            "Maintain separate collection strictly isolated from all regular domestic waste streams.",
            "Rely exclusively on certified chemical neutralization or high-temperature hazardous incineration."
        ],
        "action_steps": [
            "Keep hazardous substances (paints, automotive fluids, pesticides, batteries, solvents) in their original tightly sealed containers.",
            "Store safely in a well-ventilated, secure area away from heat sources, children, and pets until collection.",
            "Deliver directly to a licensed municipal hazardous-waste station or schedule an authorized hazardous pickup."
        ],
        "precautions": [
            "Do not dispose of hazardous materials in normal household bins, curbside recycling, or street gutters.",
            "Never pour solvents, motor oil, bleach, or paints down sinks, toilets, or outdoor storm drains.",
            "Avoid direct skin or eye contact and inhalation of vapors; use chemical-resistant gloves when handling."
        ],
        "environmental_impact": "Professional hazardous waste management prevents lethal biological and chemical contamination of groundwater aquifers, rivers, and community topsoil.",
        "recyclable": False,
        "collection_recommended": True,
    },
    WasteType.OTHER.value: {
        "category": WasteType.OTHER.value,
        "primary_method": "Unable to confidently identify this item",
        "recycling_methods": [
            "Unable to confidently identify this item: do not assume or invent an unverified recycling method.",
            "Ask the user to verify the item and check packaging for resin identification codes or material composition stamps.",
            "Recommend checking the product or manufacturer label for disposal and recycling directions.",
            "Offer administrator or municipal collection assistance if the waste type remains uncertain."
        ],
        "action_steps": [
            "Inspect the item for recycling triangles, material abbreviations (PET, PP, PAP, FE), or disposal labels.",
            "If the item is confirmed to be non-recyclable composite or soiled waste, dispose of it in the residual landfill bin.",
            "Submit a collection request through this system to have an administrator or sanitation specialist inspect the item."
        ],
        "precautions": [
            "Do not guess or assume an unidentified item is recyclable or compostable without positive identification.",
            "Never burn, bury, or dump unidentified materials in public spaces or storm drains.",
            "Avoid handling sharp, leaking, or suspicious unknown substances without protective equipment."
        ],
        "environmental_impact": "Taking time to verify uncertain items prevents cross-contamination of clean recyclable bales and avoids introducing hazardous substances into standard recycling plants.",
        "recyclable": False,
        "collection_recommended": True,
    },
}


def get_recycling_guidance(waste_type: str, is_low_confidence: bool = False) -> Dict[str, Any]:
    """Retrieve structured recycling methods and disposal recommendations.

    Returns:
    {
        "category": str,
        "primary_method": str,
        "recycling_methods": List[str],
        "action_steps": List[str],
        "precautions": List[str],
        "environmental_impact": str,
        "recyclable": bool,
        "collection_recommended": bool,
    }
    """
    if is_low_confidence:
        guidance = RECYCLING_GUIDANCE_CATALOG[WasteType.OTHER.value].copy()
        guidance["category"] = WasteType.OTHER.value
        return guidance

    normalized_type = (waste_type or "").strip()
    for key, data in RECYCLING_GUIDANCE_CATALOG.items():
        if key.lower() == normalized_type.lower():
            return data.copy()

    fallback = RECYCLING_GUIDANCE_CATALOG[WasteType.OTHER.value].copy()
    fallback["category"] = waste_type or WasteType.OTHER.value
    return fallback
