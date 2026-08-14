from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from src.services.providers.base import BaseTranslationProvider


SYSTEM_PROMPT = (
    "You are a professional, highly accurate translation engine. "
    "Translate the user's input text accurately and naturally into {target_lang}. "
    "Preserve formatting, line breaks, code blocks, emojis, and punctuation. "
    "Output ONLY the translated text. Do NOT add any preamble, explanations, notes, or quotes."
)


class DeepSeekProvider(BaseTranslationProvider):
    name = "deepseek"
    supports_streaming = True
    default_model = "deepseek-chat"
    base_url = "https://api.deepseek.com"

    def _get_client(self, api_key: str) -> AsyncOpenAI:
        if not api_key:
            raise ValueError("DeepSeek API Key is not configured. Please set it in /settings.")
        return AsyncOpenAI(api_key=api_key.strip(), base_url=self.base_url)

    async def translate(
        self,
        text: str,
        source_lang: Optional[str],
        target_lang: str,
        api_key: str,
    ) -> str:
        client = self._get_client(api_key)
        prompt = SYSTEM_PROMPT.format(target_lang=target_lang)

        response = await client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    async def translate_stream(
        self,
        text: str,
        source_lang: Optional[str],
        target_lang: str,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        client = self._get_client(api_key)
        prompt = SYSTEM_PROMPT.format(target_lang=target_lang)

        stream = await client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
