"""Prompt design for constrained gloss-to-English rewriting."""

from __future__ import annotations

import json
from typing import Any

PROMPT_VERSION = "signbridge-gloss-rewrite-v1"

SYSTEM_PROMPT = """You are Signbridge's constrained gloss-to-English rewriting component.

You rewrite recognised BSL gloss tokens into one clear English sentence for a public-service appointment demo.

Safety rules:
- Use only facts present in the tokens, scenario, and token glossary.
- Do not add policy advice, legal rights, clinical claims, dates, names, timeframes, diagnoses, sources, promises, or obligations.
- Do not infer severity unless a severity token is present.
- If the tokens are incomplete or ambiguous, write a confirmation-style sentence instead of filling gaps.
- Output strict JSON only: {"text":"...","unsupported_facts":[]}.
- If you cannot comply without adding facts, set text to a confirmation-style sentence and list the unsupported facts you avoided.
"""

TOKEN_GLOSSARY = {
    "MY_HOME": "my home",
    "NEED": "I need",
    "WANT": "I want",
    "DAMP": "damp",
    "MOULD": "mould",
    "CHILD": "a child",
    "CHILD_ASTHMA": "my child's asthma",
    "ASTHMA": "asthma",
    "REPAIR": "repair",
    "URGENT": "urgent",
    "APPOINTMENT": "appointment",
    "INTERPRETER": "BSL interpreter",
    "WRITING": "in writing",
    "COMPLAINT": "complaint",
    "EVIDENCE": "evidence",
    "PHOTO": "photo evidence",
    "INSPECTION": "inspection",
    "NEXT_STEP": "next step",
    "COUNCIL": "the council",
    "CALL_BACK": "call back",
    "ACCESS_SUPPORT": "accessible communication support",
    "NOT_UNDERSTAND": "I do not understand",
    "PLEASE_REPEAT": "please repeat",
    "CONFIRM": "confirm",
    "DATE": "date",
    "BEDROOM": "bedroom",
    "LEAK": "leak",
    "WALL": "wall",
}


def build_gloss_messages(
    *,
    tokens: list[str],
    scenario: str,
    confidence: float,
) -> list[dict[str, Any]]:
    glossary = {token: TOKEN_GLOSSARY.get(token, token.replace("_", " ").lower()) for token in tokens}
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "prompt_version": PROMPT_VERSION,
                    "scenario": scenario,
                    "recognition_confidence": confidence,
                    "tokens": tokens,
                    "token_glossary": glossary,
                    "output_contract": {
                        "text": "single sentence, max 220 characters",
                        "unsupported_facts": "array of facts the model refused to invent",
                    },
                },
                separators=(",", ":"),
            ),
        },
    ]
