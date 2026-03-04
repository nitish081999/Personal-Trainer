import json
import logging
import time
from datetime import date
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class APIUsageTracker:
    """Track daily API usage across providers."""

    def __init__(self):
        self._usage: dict[str, dict[str, int]] = {}
        self._current_date: str = ""
        self._reset_if_new_day()

    def _reset_if_new_day(self):
        today = date.today().isoformat()
        if today != self._current_date:
            self._current_date = today
            self._usage = {
                "groq": {"tokens": 0, "calls": 0},
                "gemini": {"tokens": 0, "calls": 0},
                "mistral": {"tokens": 0, "calls": 0},
            }

    def record(self, provider: str, tokens: int = 0):
        self._reset_if_new_day()
        if provider in self._usage:
            self._usage[provider]["tokens"] += tokens
            self._usage[provider]["calls"] += 1

    def can_use(self, provider: str) -> bool:
        self._reset_if_new_day()
        if provider == "groq":
            return self._usage["groq"]["tokens"] < settings.GROQ_DAILY_TOKEN_LIMIT
        elif provider == "gemini":
            return self._usage["gemini"]["calls"] < settings.GEMINI_DAILY_CALL_LIMIT
        elif provider == "mistral":
            return self._usage["mistral"]["tokens"] < settings.MISTRAL_DAILY_TOKEN_LIMIT
        return False

    def get_usage(self) -> dict:
        self._reset_if_new_day()
        return {
            "groq_tokens_used": self._usage["groq"]["tokens"],
            "groq_daily_limit": settings.GROQ_DAILY_TOKEN_LIMIT,
            "gemini_calls_used": self._usage["gemini"]["calls"],
            "gemini_daily_limit": settings.GEMINI_DAILY_CALL_LIMIT,
            "mistral_tokens_used": self._usage["mistral"]["tokens"],
            "mistral_daily_limit": settings.MISTRAL_DAILY_TOKEN_LIMIT,
        }


usage_tracker = APIUsageTracker()


async def _call_groq(prompt: str, system_prompt: str = "", model: str = "llama-3.3-70b-versatile") -> Optional[str]:
    """Call Groq API."""
    if not settings.GROQ_API_KEY or not usage_tracker.can_use("groq"):
        return None

    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            tokens = data.get("usage", {}).get("total_tokens", 0)
            usage_tracker.record("groq", tokens)
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return None


async def _call_gemini(prompt: str, system_prompt: str = "") -> Optional[str]:
    """Call Google Gemini API."""
    if not settings.GEMINI_API_KEY or not usage_tracker.can_use("gemini"):
        return None

    try:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}",
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 4096,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
            usage_tracker.record("gemini", 0)
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        return None
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


async def _call_mistral(prompt: str, system_prompt: str = "") -> Optional[str]:
    """Call Mistral API."""
    if not settings.MISTRAL_API_KEY or not usage_tracker.can_use("mistral"):
        return None

    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mistral-small-latest",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            tokens = data.get("usage", {}).get("total_tokens", 0)
            usage_tracker.record("mistral", tokens)
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        return None


class LLMRouter:
    """Route LLM calls to appropriate provider with fallback."""

    @staticmethod
    async def generate_mcq(prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generate MCQs - Primary: Groq, Fallback: Mistral, then Gemini."""
        result = await _call_groq(prompt, system_prompt)
        if result:
            return result
        result = await _call_mistral(prompt, system_prompt)
        if result:
            return result
        return await _call_gemini(prompt, system_prompt)

    @staticmethod
    async def explain(prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generate explanations - Primary: Gemini, Fallback: Groq."""
        result = await _call_gemini(prompt, system_prompt)
        if result:
            return result
        return await _call_groq(prompt, system_prompt)

    @staticmethod
    async def structure_json(prompt: str, system_prompt: str = "") -> Optional[str]:
        """Structure content as JSON - Primary: Gemini, Fallback: Mistral."""
        result = await _call_gemini(prompt, system_prompt)
        if result:
            return result
        result = await _call_mistral(prompt, system_prompt)
        if result:
            return result
        return await _call_groq(prompt, system_prompt)

    @staticmethod
    async def generate_similar(prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generate similar questions - Primary: Groq, Fallback: Gemini."""
        result = await _call_groq(prompt, system_prompt)
        if result:
            return result
        return await _call_gemini(prompt, system_prompt)

    @staticmethod
    async def concept_deep_dive(prompt: str, system_prompt: str = "") -> Optional[str]:
        """Deep concept explanation - Primary: Gemini, Fallback: Mistral."""
        result = await _call_gemini(prompt, system_prompt)
        if result:
            return result
        return await _call_mistral(prompt, system_prompt)

    @staticmethod
    async def generic_call(prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generic LLM call with full fallback chain."""
        result = await _call_groq(prompt, system_prompt)
        if result:
            return result
        result = await _call_gemini(prompt, system_prompt)
        if result:
            return result
        return await _call_mistral(prompt, system_prompt)


def extract_json_from_response(text: str) -> Optional[list | dict]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    if not text:
        return None

    # Try to find JSON in code blocks
    import re
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if json_match:
        text = json_match.group(1).strip()

    # Try to find JSON array or object
    for start_char, end_char in [("[", "]"), ("{", "}")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue

    # Last resort: try parsing the whole text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


llm_router = LLMRouter()
