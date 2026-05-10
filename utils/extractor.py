"""
utils/extractor.py
Extract factual claims from document text using Groq API (free).
"""

import json
import streamlit as st
import re
from groq import Groq


EXTRACTION_PROMPT = """You are a precise fact-extraction engine.

Given the following document text, extract all verifiable factual claims.
Focus on:
- Statistics and percentages (e.g. "GDP grew by 7%")
- Named entities with attributes (e.g. "Tesla was founded in 2003")
- Dates and timelines
- Financial figures
- Scientific or technical statements
- Population or demographic data
- Rankings or comparisons

Return ONLY a valid JSON array. Each element must have:
  "claim": the exact factual statement (string)
  "type": one of ["statistic", "date", "financial", "scientific", "demographic", "ranking", "other"]

Extract between 5 and 20 claims. Do not include opinions or subjective statements.
Do not include any explanation or markdown — only the raw JSON array.

Document text:
\"\"\"
{text}
\"\"\"
"""


def extract_claims(text: str, api_key: str) -> list[dict]:
    """
    Uses Groq (Llama 3) to extract factual claims from the provided text.
    Returns a list of dicts: [{claim, type}, ...]
    """
    client = Groq(api_key=api_key)

    # Truncate if very long to stay within token limits
    truncated = text[:12000] if len(text) > 12000 else text

    prompt = EXTRACTION_PROMPT.format(text=truncated)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        claims = json.loads(raw)

        # Normalise: ensure each item is a dict with a 'claim' key
        normalised = []
        for item in claims:
            if isinstance(item, dict) and "claim" in item:
                normalised.append(item)
            elif isinstance(item, str):
                normalised.append({"claim": item, "type": "other"})

        return normalised

    except json.JSONDecodeError:
        lines = [ln.strip("- •*").strip() for ln in raw.split("\n") if ln.strip()]
        return [{"claim": ln, "type": "other"} for ln in lines if len(ln) > 20]

    except Exception as e:
    st.error(f"Claim extraction failed: {e}")
    return []