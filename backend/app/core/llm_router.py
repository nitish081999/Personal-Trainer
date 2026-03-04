import time
import logging

class RateLimitExceeded(Exception):
    pass

class LLMRouter:
    def __init__(self):
        # In a real app, this should be tracked in a DB/Redis
        self.api_usage_tracker = {
            "groq": {"daily_tokens": 0, "calls": 0, "cooldown_until": 0},
            "gemini": {"daily_tokens": 0, "calls": 0, "cooldown_until": 0},
            "mistral": {"daily_tokens": 0, "calls": 0, "cooldown_until": 0}
        }
        self.daily_limits = {
            "groq": 500000,
            "gemini": 1500, # tracking calls
            "mistral": 500000
        }

    def _check_rate_limit(self, provider: str) -> bool:
        if time.time() < self.api_usage_tracker[provider]["cooldown_until"]:
            return False
            
        if provider == "gemini":
            if self.api_usage_tracker[provider]["calls"] >= self.daily_limits[provider]:
                self.api_usage_tracker[provider]["cooldown_until"] = time.time() + 3600 # 1 hr cooldown
                return False
        else:
            if self.api_usage_tracker[provider]["daily_tokens"] >= self.daily_limits[provider]:
                self.api_usage_tracker[provider]["cooldown_until"] = time.time() + 3600
                return False
        return True

    def _log_usage(self, provider: str, tokens: int = 0):
        self.api_usage_tracker[provider]["daily_tokens"] += tokens
        self.api_usage_tracker[provider]["calls"] += 1
        
    def _groq_call(self, prompt: str):
        if not self._check_rate_limit("groq"):
            raise RateLimitExceeded("Groq rate limit exceeded")
        # Placeholder for actual Groq API call
        self._log_usage("groq", tokens=len(prompt))
        return {"response": f"Groq response for: {prompt[:20]}", "provider": "groq"}

    def _mistral_call(self, prompt: str):
        if not self._check_rate_limit("mistral"):
            raise RateLimitExceeded("Mistral rate limit exceeded")
        # Placeholder for actual Mistral API call
        self._log_usage("mistral", tokens=len(prompt))
        return {"response": f"Mistral response for: {prompt[:20]}", "provider": "mistral"}

    def _gemini_call(self, prompt: str):
        if not self._check_rate_limit("gemini"):
            raise RateLimitExceeded("Gemini rate limit exceeded")
        # Placeholder for actual Gemini API call
        self._log_usage("gemini", tokens=len(prompt))
        return {"response": f"Gemini response for: {prompt[:20]}", "provider": "gemini"}

    def generate_mcq(self, prompt: str):
        try:
            return self._groq_call(prompt)
        except RateLimitExceeded as e:
            logging.warning(f"Groq failed: {e}. Falling back to Mistral.")
            return self._mistral_call(prompt)

    def explain(self, prompt: str):
        try:
            return self._gemini_call(prompt)
        except RateLimitExceeded as e:
            logging.warning(f"Gemini failed: {e}. Falling back to Groq.")
            return self._groq_call(prompt)
            
    def structure_json(self, prompt: str):
        try:
            return self._gemini_call(prompt)
        except RateLimitExceeded as e:
            logging.warning(f"Gemini failed: {e}. Falling back to Mistral.")
            return self._mistral_call(prompt)
