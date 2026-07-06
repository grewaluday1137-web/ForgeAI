import logging
from src.agents.providers.base import AIProvider
from src.core.config import settings

logger = logging.getLogger(__name__)

_provider_instance: AIProvider | None = None


def get_provider() -> AIProvider:
    """
    Factory function — returns the appropriate AI provider based on configuration.
    Uses a singleton pattern to avoid re-initializing on every request.
    
    Returns:
        GeminiProvider if GEMINI_API_KEY is configured.
        MockProvider otherwise (safe fallback for development).
    """
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    if settings.MOCK_AI:
        logger.info("AI Provider: MOCK_AI=true — Using MockProvider")
        from src.agents.providers.mock import MockProvider
        _provider_instance = MockProvider()
    elif settings.GROQ_API_KEY:
        logger.info("AI Provider: Using GroqProvider")
        from src.agents.providers.groq import GroqProvider
        _provider_instance = GroqProvider()
    elif settings.OPENROUTER_API_KEY:
        logger.info("AI Provider: Using OpenRouterProvider")
        from src.agents.providers.openrouter import OpenRouterProvider
        _provider_instance = OpenRouterProvider()
    elif settings.GEMINI_API_KEY:
        logger.info("AI Provider: Using GeminiProvider (gemini-2.0-flash)")
        from src.agents.providers.gemini import GeminiProvider
        _provider_instance = GeminiProvider()
    else:
        logger.warning("AI Provider: No API keys set — falling back to MockProvider")
        from src.agents.providers.mock import MockProvider
        _provider_instance = MockProvider()

    return _provider_instance
