from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class BaseTranslationProvider(ABC):
    name: str = "base"
    supports_streaming: bool = False

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: Optional[str],
        target_lang: str,
        api_key: str,
    ) -> str:
        """Translates text synchronously/in a single request."""
        pass

    async def translate_stream(
        self,
        text: str,
        source_lang: Optional[str],
        target_lang: str,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        """
        Streams translation chunks as they become available.
        Default implementation yields the complete translation at once.
        """
        result = await self.translate(text, source_lang, target_lang, api_key)
        yield result
