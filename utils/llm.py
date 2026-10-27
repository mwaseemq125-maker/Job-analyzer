"""LLM factory supporting Google Gemini and Groq."""

from __future__ import annotations

import config
from exceptions import ConfigurationError


def get_llm(temperature: float = 0.0):
    """Build a chat model for the currently selected provider."""
    provider = config.get_provider()
    api_key = config.get_api_key(provider)
    model = config.get_model(provider)

    if not api_key:
        raise ConfigurationError(
            f"Missing API key. Set {config.API_KEY_ENV[provider]} in your .env file "
            f"(or enter it in the sidebar) to use {provider.title()}."
        )

    try:
        if provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=model, temperature=temperature, google_api_key=api_key
            )

        from langchain_groq import ChatGroq

        return ChatGroq(model=model, temperature=temperature, api_key=api_key)
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ConfigurationError(
            f"Missing dependency for {provider}: {exc}. Run `pip install -r requirements.txt`."
        ) from exc
