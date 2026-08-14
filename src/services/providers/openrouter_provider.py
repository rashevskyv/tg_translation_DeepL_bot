from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from src.services.providers.base import BaseTranslationProvider


SYSTEM_PROMPT = (
    "You are a professional, highly accurate translation engine. "
    "Translate the user's input text accurately and naturally into {target_lang}. "
    "Preserve formatting, line breaks, code blocks, emojis, and punctuation. "
    "Output ONLY the translated text. Do NOT include reasoning, thinking traces, preambles, explanations, notes, or quotes."
)


class OpenRouterProvider(BaseTranslationProvider):
    supports_streaming = True
    base_url = "https://openrouter.ai/api/v1"

    def __init__(self, name: str, model_id: str):
        self.name = name
        self.model_id = model_id

    def _get_client(self, api_key: str) -> AsyncOpenAI:
        if not api_key:
            raise ValueError(
                f"OpenRouter API Key is not configured for {self.name}.\n"
                f"Please add your OpenRouter key in /settings or set OPENROUTER_API_KEY in .env."
            )
        return AsyncOpenAI(
            api_key=api_key.strip(),
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/rashevskyv/tg_translation_DeepL_bot",
                "X-Title": "Telegram Translation Bot",
            },
        )

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
            model=self.model_id,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        return content.strip()

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
            model=self.model_id,
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
