import json
import logging
import re
from typing import NamedTuple, Optional
from openai import AsyncOpenAI
from src.config import PROVIDERS_INFO

logger = logging.getLogger(__name__)


class AssistantDecision(NamedTuple):
    status: str  # "ready" or "needs_clarification"
    question: Optional[str]
    translation: Optional[str]


ASSISTANT_SYSTEM_PROMPT = """You are an expert bilingual translation assistant.
Your goal is to ensure the translation from {source_lang} to {target_lang} conveys the user's exact intended meaning, nuances, tone, and context.

Analyze the user's input:
1. If the text contains ambiguity, multiple possible interpretations, slang/idioms, vague pronouns, or multiple tone styles (e.g. formal vs informal, technical vs casual):
   Respond with:
   {{
     "status": "needs_clarification",
     "question": "<A concise, polite clarification question in Ukrainian pointing out the specific ambiguity and offering 2-3 clear options>",
     "translation": null
   }}
2. If the text is 100% clear, unambiguous, and straightforward:
   Respond with:
   {{
     "status": "ready",
     "question": null,
     "translation": "<Accurate, natural translation in {target_lang}>"
   }}

Output ONLY the valid JSON object without any additional text, markdown fences, or reasoning.
"""

CLARIFIED_TRANSLATION_PROMPT = """You are an expert bilingual translation assistant.
The user wanted to translate text from {source_lang} to {target_lang}.
Original text: "{original_text}"
Clarification details provided by user: "{user_clarification}"

Produce a concise, high-quality, perfectly natural translation in {target_lang} incorporating all clarified nuances and style.
Output ONLY the final translated text. Do NOT include any explanations, notes, or quotes.
"""


class AssistantService:
    async def analyze_and_process(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        provider_name: str,
        api_key: str,
    ) -> AssistantDecision:
        """
        Analyzes the text for ambiguity using the chosen assistant model.
        Returns AssistantDecision with either direct translation or clarification question.
        """
        model_id = PROVIDERS_INFO.get(provider_name, {}).get("model", "google/gemini-3.7-flash")
        client = AsyncOpenAI(
            api_key=api_key.strip(),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/rashevskyv/tg_translation_DeepL_bot",
                "X-Title": "TG Translation Bot",
            },
        )

        prompt = ASSISTANT_SYSTEM_PROMPT.format(source_lang=source_lang, target_lang=target_lang)

        try:
            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.2,
                extra_body={"reasoning": {"effort": "none"}},
            )
            raw_content = response.choices[0].message.content or ""
            clean_json = re.sub(r"^```(?:json)?\s*", "", raw_content.strip(), flags=re.IGNORECASE)
            clean_json = re.sub(r"\s*```$", "", clean_json.strip())

            data = json.loads(clean_json)
            status = data.get("status", "ready")
            question = data.get("question")
            translation = data.get("translation")

            if status == "needs_clarification" and question:
                return AssistantDecision(status="needs_clarification", question=question.strip(), translation=None)
            elif translation:
                return AssistantDecision(status="ready", question=None, translation=translation.strip())
        except Exception as e:
            logger.warning(f"Assistant analysis failed, falling back to direct translation: {e}")

        return AssistantDecision(status="ready", question=None, translation=None)

    async def finalize_clarified_translation(
        self,
        original_text: str,
        user_clarification: str,
        source_lang: str,
        target_lang: str,
        provider_name: str,
        api_key: str,
    ) -> str:
        """Generates the final translation after user clarified their intent."""
        model_id = PROVIDERS_INFO.get(provider_name, {}).get("model", "google/gemini-3.7-flash")
        client = AsyncOpenAI(
            api_key=api_key.strip(),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/rashevskyv/tg_translation_DeepL_bot",
                "X-Title": "TG Translation Bot",
            },
        )

        system_msg = CLARIFIED_TRANSLATION_PROMPT.format(
            source_lang=source_lang,
            target_lang=target_lang,
            original_text=original_text,
            user_clarification=user_clarification,
        )

        response = await client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Clarification: {user_clarification}"},
            ],
            temperature=0.2,
            extra_body={"reasoning": {"effort": "none"}},
        )
        return (response.choices[0].message.content or "").strip()


assistant_service = AssistantService()
