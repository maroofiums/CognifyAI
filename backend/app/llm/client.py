"""Thin wrapper around LangChain's ChatMistralAI for optional LLM enrichment.

All pipeline stages work without an LLM (using deterministic heuristics).
When ``settings.USE_LLM`` is true and ``MISTRAL_API_KEY`` is set, this module
provides a single helper, :func:`call_llm_json`, which sends a prompt and
parses the JSON response.
"""
from __future__ import annotations

from typing import Optional

from app.core.config import settings
from app.utils.helpers import safe_json_loads

_llm = None


def _get_llm():
    """Lazily construct and cache a LangChain ChatMistralAI instance."""
    global _llm
    if _llm is not None:
        return _llm

    if not settings.USE_LLM or not settings.MISTRAL_API_KEY:
        return None

    try:
        from langchain_mistralai import ChatMistralAI

        _llm = ChatMistralAI(
            model=settings.LLM_MODEL,
            api_key=settings.MISTRAL_API_KEY,
            temperature=0.1,
        )
        return _llm
    except Exception:
        # If langchain/mistral isn't reachable or misconfigured, silently
        # disable LLM enrichment and fall back to heuristics.
        return None


def is_llm_enabled() -> bool:
    return _get_llm() is not None


def call_llm_json(prompt: str) -> Optional[dict]:
    """Send ``prompt`` to the configured LLM and parse the JSON response.

    Returns ``None`` if the LLM is not configured or the call fails, so
    callers can transparently fall back to heuristic implementations.
    """
    llm = _get_llm()
    if llm is None:
        return None

    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        return safe_json_loads(content)
    except Exception:
        return None
