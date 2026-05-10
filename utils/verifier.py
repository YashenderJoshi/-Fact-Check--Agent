"""
utils/verifier.py
Verify claims using Groq's built-in knowledge (no web search dependency).
Falls back to DuckDuckGo only if available.
"""

import json
import re
import time
from groq import Groq

try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False


VERIFICATION_PROMPT = """You are a rigorous fact-checking assistant with extensive knowledge.

A document makes the following claim:
CLAIM: "{claim}"

{evidence_section}

Using your knowledge, carefully evaluate this claim.

Respond ONLY with a valid JSON object. No markdown, no explanation, just raw JSON:
{{
  "status": "Verified" or "Inaccurate" or "False",
  "corrected_fact": "if Verified write the claim as-is; if Inaccurate or False write the correct fact",
  "source": "mention your knowledge source e.g. World Bank, IMF, Wikipedia",
  "confidence": "High" or "Medium" or "Low"
}}

Rules:
- Verified = claim is accurate based on your knowledge
- Inaccurate = claim has wrong figures but is partially correct
- False = claim is completely wrong or fabricated
- If you are not sure, use confidence "Low" but still give your best verdict
- Never say "No information available" — always give a real corrected fact
"""


def search_web(query: str, max_results: int = 3) -> str:
    """Try DuckDuckGo search, return empty string if it fails."""
    if not DDG_AVAILABLE:
        return ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return ""
        snippets = []
        for r in results:
            title = r.get("title", "")
            body  = r.get("body", "")
            snippets.append(f"• [{title}] {body}")
        return "\n".join(snippets)
    except Exception:
        return ""


def verify_claims(claim_obj: dict | str, api_key: str) -> dict:
    """
    Verify a claim using Groq's knowledge, optionally enriched with web search.
    Returns: {claim, status, corrected_fact, source, confidence}
    """
    if isinstance(claim_obj, dict):
        claim_text = claim_obj.get("claim", str(claim_obj))
    else:
        claim_text = str(claim_obj)

    # Try web search (optional enrichment)
    evidence = search_web(claim_text)
    if evidence:
        evidence_section = f"Here is additional evidence from the web:\n---\n{evidence}\n---\n"
    else:
        evidence_section = "Use your own knowledge to verify this claim.\n"

    prompt = VERIFICATION_PROMPT.format(
        claim=claim_text,
        evidence_section=evidence_section
    )

    client = Groq(api_key=api_key)

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fact-checking assistant. Always respond with a single valid JSON object only. No markdown fences, no extra text."
                    },
                    {"role": "user", "content": prompt}
                ]
            )

            raw = response.choices[0].message.content.strip()

            # Strip markdown fences
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            # Extract first JSON object found
            match = re.search(r'\{.*?\}', raw, re.DOTALL)
            if match:
                raw = match.group(0)

            verdict = json.loads(raw)

            status = verdict.get("status", "Inaccurate")
            if status not in ["Verified", "Inaccurate", "False"]:
                status = "Inaccurate"

            corrected = verdict.get("corrected_fact", "")
            if not corrected or "no information" in corrected.lower():
                corrected = claim_text  # fallback to original

            return {
                "claim":          claim_text,
                "status":         status,
                "corrected_fact": corrected,
                "source":         verdict.get("source", "Groq / LLM Knowledge"),
                "confidence":     verdict.get("confidence", "Medium"),
            }

        except (json.JSONDecodeError, KeyError):
            if attempt < 2:
                time.sleep(1)
                continue
            # Last resort: scan text for status keyword
            raw_lower = raw.lower() if 'raw' in dir() else ""
            if "verified" in raw_lower:
                status = "Verified"
            elif "false" in raw_lower:
                status = "False"
            else:
                status = "Inaccurate"
            return {
                "claim":          claim_text,
                "status":         status,
                "corrected_fact": "Could not parse AI response.",
                "source":         "",
                "confidence":     "Low",
            }

        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            return {
                "claim":          claim_text,
                "status":         "Inaccurate",
                "corrected_fact": f"API error: {str(e)[:80]}",
                "source":         "",
                "confidence":     "Low",
            }