"""Unified LLM service that supports multiple providers."""

import json
from typing import Optional
from anthropic import Anthropic
from openai import OpenAI
import httpx

from app.config import settings


class LLMService:
    """Unified interface for multiple LLM providers."""

    def __init__(self):
        self.provider = settings.llm_provider.lower()

        # Initialize based on provider
        if self.provider == "anthropic":
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model
            self.max_tokens = settings.anthropic_max_tokens
        elif self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            self.max_tokens = settings.openai_max_tokens
        elif self.provider == "openrouter":
            self.client = OpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = settings.openrouter_model
            self.max_tokens = settings.openrouter_max_tokens
        elif self.provider == "lmstudio":
            # LMStudio custom /chat endpoint
            self.client = None  # Use httpx directly
            self.model = settings.lmstudio_model
            self.max_tokens = settings.lmstudio_max_tokens
            self.base_url = settings.lmstudio_base_url
        elif self.provider == "ollama":
            self.client = None  # Ollama uses httpx directly
            self.model = settings.ollama_model
            self.max_tokens = settings.ollama_max_tokens
            self.base_url = settings.ollama_base_url
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> tuple[str, dict]:
        """
        Generate completion from LLM.

        Returns:
            tuple: (response_text, usage_dict)
        """
        if self.provider == "anthropic":
            return await self._anthropic_completion(prompt, system_prompt)
        elif self.provider == "lmstudio":
            return await self._lmstudio_completion(prompt, system_prompt)
        elif self.provider in ["openai", "openrouter"]:
            return await self._openai_compatible_completion(prompt, system_prompt)
        elif self.provider == "ollama":
            return await self._ollama_completion(prompt, system_prompt)

    async def _anthropic_completion(self, prompt: str, system_prompt: Optional[str] = None) -> tuple[str, dict]:
        """Generate completion using Anthropic Claude."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        message = self.client.messages.create(**kwargs)

        # Handle usage stats (may be None for some providers)
        usage = {
            "input_tokens": getattr(message.usage, 'input_tokens', 0) if message.usage else 0,
            "output_tokens": getattr(message.usage, 'output_tokens', 0) if message.usage else 0,
            "total_tokens": 0
        }
        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]

        return message.content[0].text, usage

    async def _openai_compatible_completion(self, prompt: str, system_prompt: Optional[str] = None) -> tuple[str, dict]:
        """Generate completion using OpenAI-compatible API (OpenAI, OpenRouter, LMStudio)."""

        # LMStudio has a different API format
        if self.provider == "lmstudio":
            return await self._lmstudio_completion(prompt, system_prompt)

        # Standard OpenAI format
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens
        )

        usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return response.choices[0].message.content, usage

    async def _lmstudio_completion(self, prompt: str, system_prompt: Optional[str] = None) -> tuple[str, dict]:
        """Generate completion using LMStudio's custom /chat endpoint."""
        url = f"{self.base_url.rstrip('/')}/chat"

        payload = {
            "model": self.model,
            "input": prompt
        }

        if system_prompt:
            payload["system_prompt"] = system_prompt

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

        # LMStudio returns: {"output": [{"type": "reasoning", ...}, {"type": "message", "content": "..."}], "stats": {...}}
        response_text = ""

        if "output" in result and isinstance(result["output"], list):
            # Find the message content (not reasoning)
            for item in result["output"]:
                if isinstance(item, dict) and item.get("type") == "message":
                    response_text = item.get("content", "")
                    break

            # Fallback to last item if no message found
            if not response_text and result["output"]:
                last_item = result["output"][-1]
                if isinstance(last_item, dict):
                    response_text = last_item.get("content", "")

        # Extract usage stats if available
        stats = result.get("stats", {})
        usage = {
            "input_tokens": stats.get("input_tokens", 0),
            "output_tokens": stats.get("total_output_tokens", 0),
            "total_tokens": stats.get("input_tokens", 0) + stats.get("total_output_tokens", 0)
        }

        return response_text, usage

    async def _ollama_completion(self, prompt: str, system_prompt: Optional[str] = None) -> tuple[str, dict]:
        """Generate completion using Ollama."""
        url = f"{self.base_url}/api/generate"

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": self.max_tokens
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

        usage = {
            "input_tokens": result.get("prompt_eval_count", 0),
            "output_tokens": result.get("eval_count", 0),
            "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
        }

        return result["response"], usage

    def parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        try:
            # Try direct parse first
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Try to extract from markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            return json.loads(response_text.strip())

    def get_provider_info(self) -> dict:
        """Get information about the current provider."""
        return {
            "provider": self.provider,
            "model": self.model,
            "max_tokens": self.max_tokens
        }
