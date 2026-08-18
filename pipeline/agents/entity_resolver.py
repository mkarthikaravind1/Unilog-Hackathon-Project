"""
Agent 1: Entity Resolver

Given one raw input row, identifies:
    - MANUFACTURER_NAME  (real manufacturer, e.g. "Whirlpool Corporation")
    - BRAND_NAME         (brand with symbols, e.g. "FRIGIDAIRE®")
    - TRADE_NAME         (if different from brand)
    - confidence         (high / medium / low)
    - needs_review       (True if uncertain)
    - reasoning          (short explanation of how it was determined)

Key insight from ground truth:
    Part_Manuf is often the DISTRIBUTOR, not the manufacturer.
    E.g. "Appliance Dealers Cooperative (APPDE)" is a distributor;
    the real manufacturer is "Rheem Manufacturing" (brand: FRIGIDAIRE®).
    So we use Part_Desc + Mfg_Part_Num to identify the real manufacturer.

This is a two-step agent:
    Step 1 - Extract brand signal from Part_Desc / Mfg_Part_Num
    Step 2 - Resolve to canonical manufacturer + brand name
"""
import json
import re
from pipeline.llm_client import call_llm
from pipeline.config import is_placeholder


# ── Prompts ────────────────────────────────────────────────────────────────

STEP1_SYSTEM = """You are a product data expert specializing in industrial and consumer products.
Your job is to extract brand and manufacturer signals from messy product descriptions.
Always respond with valid JSON only. No explanation, no markdown, no code fences."""

STEP1_USER_TEMPLATE = """Analyze this raw product record and extract brand/manufacturer signals.

Input:
  Mfg_Part_Num : {mfg_part_num}
  Part_Desc    : {part_desc}
  Part_Manuf   : {part_manuf}
  E1_Brand     : {e1_brand}
  Unilog_Brand : {unilog_brand}
  DIB_Brand    : {dib_brand}

IMPORTANT RULES:
1. Part_Manuf is often a DISTRIBUTOR, not the actual manufacturer. Look at Part_Desc and Mfg_Part_Num for the real brand.
2. The brand name in Part_Desc (e.g. "3M", "FRIGIDAIRE", "Diablo") is the strongest signal.
3. Extract the brand signal even if it appears only as a prefix in the part number or description.

Respond with this exact JSON:
{{
  "brand_signal": "the brand name you detected (e.g. '3M', 'Frigidaire', 'Diablo')",
  "brand_source": "where you found it: 'part_desc' | 'part_num' | 'e1_brand' | 'unilog_brand' | 'dib_brand' | 'part_manuf' | 'unknown'",
  "part_manuf_is_distributor": true or false,
  "product_type": "what kind of product this is (e.g. 'Sanding Belt', 'Dishwasher', 'Pipe Fitting')",
  "reasoning": "one sentence explaining your decision"
}}"""


STEP2_SYSTEM = """You are a product data expert with deep knowledge of industrial manufacturers and consumer brands.
Your job is to resolve a brand signal into the canonical manufacturer name and brand name as they appear in official records.
Always include trademark symbols (® or ™) where appropriate.
Always respond with valid JSON only. No explanation, no markdown, no code fences."""

STEP2_USER_TEMPLATE = """Resolve this brand signal to its canonical manufacturer and brand name.

Brand signal detected : {brand_signal}
Product type         : {product_type}
Part number          : {mfg_part_num}
Raw Part_Manuf field : {part_manuf}

Your job:
1. Identify the MANUFACTURER_NAME: the legal company entity that makes this product.
   Examples: "Whirlpool Corporation", "3M Company", "Freud America Inc"
2. Identify the BRAND_NAME: the brand label on the product, with trademark symbols.
   Examples: "FRIGIDAIRE®", "Whirlpool®", "Diablo®", "3M™"
   Note: Sometimes the manufacturer and brand are the same company (e.g. 3M).
3. Identify TRADE_NAME if there is a sub-brand or product line brand (e.g. "CleanBoost™").
   Leave blank if none.
4. Rate your confidence: "high" if you are certain, "medium" if likely, "low" if guessing.

Respond with this exact JSON:
{{
  "MANUFACTURER_NAME": "exact legal manufacturer name",
  "BRAND_NAME": "brand name with ® or ™ symbol if applicable",
  "TRADE_NAME": "sub-brand or trade name if any, else empty string",
  "confidence": "high | medium | low",
  "needs_review": true or false,
  "reasoning": "one sentence explaining your resolution"
}}"""


# ── JSON parser ─────────────────────────────────────────────────────────────

def _parse_json(text: str) -> dict:
    """Extracts JSON from LLM response, handles minor formatting issues."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON:\n{text}\nError: {e}")


# ── Main agent function ──────────────────────────────────────────────────────

def resolve_entity(row: dict) -> dict:
    """
    Resolves manufacturer and brand for one input row.

    Args:
        row: dict with keys from the input CSV
             (Mfg_Part_Num, Part_Desc, E1_Brand, Unilog_Brand,
              DIB_Brand, Part_Manuf, Manufacturer_Clean)

    Returns:
        dict with keys:
            MANUFACTURER_NAME, BRAND_NAME, TRADE_NAME,
            confidence, needs_review, reasoning,
            _step1  (raw step 1 result for traceability)
    """
    def safe(key):
        val = row.get(key)
        if val is None or is_placeholder(str(val)):
            return "N/A"
        return str(val).strip()

    # ── Step 1: Extract brand signal ────────────────────────────────────────
    step1_prompt = STEP1_USER_TEMPLATE.format(
        mfg_part_num=safe("Mfg_Part_Num"),
        part_desc=safe("Part_Desc"),
        part_manuf=safe("Part_Manuf"),
        e1_brand=safe("E1_Brand"),
        unilog_brand=safe("Unilog_Brand"),
        dib_brand=safe("DIB_Brand"),
    )

    step1_raw = call_llm(system=STEP1_SYSTEM, user=step1_prompt)
    step1 = _parse_json(step1_raw)

    brand_signal = step1.get("brand_signal", "unknown")
    product_type = step1.get("product_type", "unknown")

    # ── Step 2: Resolve to canonical names ──────────────────────────────────
    step2_prompt = STEP2_USER_TEMPLATE.format(
        brand_signal=brand_signal,
        product_type=product_type,
        mfg_part_num=safe("Mfg_Part_Num"),
        part_manuf=safe("Part_Manuf"),
    )

    step2_raw = call_llm(system=STEP2_SYSTEM, user=step2_prompt)
    step2 = _parse_json(step2_raw)

    return {
        "MANUFACTURER_NAME": step2.get("MANUFACTURER_NAME", ""),
        "BRAND_NAME": step2.get("BRAND_NAME", ""),
        "TRADE_NAME": step2.get("TRADE_NAME", ""),
        "confidence": step2.get("confidence", "low"),
        "needs_review": step2.get("needs_review", True),
        "reasoning": step2.get("reasoning", ""),
        "_step1": step1,  # kept for traceability / debugging
    }


def resolve_entity_batch(rows: list[dict], verbose: bool = True) -> list[dict]:
    """
    Runs resolve_entity on a list of input rows.
    Returns list of result dicts in the same order.
    """
    results = []
    for i, row in enumerate(rows):
        if verbose:
            print(f"  [{i+1}/{len(rows)}] {row.get('Mfg_Part_Num', '?')} "
                  f"| {row.get('Part_Desc', '')[:50]}")
        try:
            result = resolve_entity(row)
            result["Mfg_Part_Num"] = row.get("Mfg_Part_Num", "")
            results.append(result)
            if verbose:
                print(f"    → {result['MANUFACTURER_NAME']} / "
                      f"{result['BRAND_NAME']} [{result['confidence']}]")
        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({
                "Mfg_Part_Num": row.get("Mfg_Part_Num", ""),
                "MANUFACTURER_NAME": "",
                "BRAND_NAME": "",
                "TRADE_NAME": "",
                "confidence": "low",
                "needs_review": True,
                "reasoning": f"Error: {str(e)}",
                "_step1": {},
            })
    return results