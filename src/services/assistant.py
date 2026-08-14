import json
import logging
import re
from typing import Dict, List, NamedTuple, Optional
from openai import AsyncOpenAI
from src.config import PROVIDERS_INFO

logger = logging.getLogger(__name__)


class AssistantTurnResult(NamedTuple):
    status: str  # "ready" (approved for translation) or "clarifying" (needs more conversation)
    assistant_message: Optional[str]  # Question or reply to the user in Ukrainian
    approved_source_text: Optional[str]  # Final agreed-upon source text to send to translator engine


ASSISTANT_SYSTEM_PROMPT = """You are an expert pre-translation assistant.
The user wants to prepare a message to be translated from {source_lang} to {target_lang}.
Your task is to analyze the user's input, context, intended tone (formal vs informal), slang, idioms, or any potential ambiguities:

OPERATING RULES:
1. If the message contains ambiguity, slang/idioms, vague pronouns, multiple potential interpretations, or tone nuances:
   Engage in a helpful conversation with the user in Ukrainian. Ask specific clarifying questions or offer options to pin down the exact intended meaning.
   Respond strictly with JSON:
   {{
     "status": "clarifying",
     "assistant_message": "<Your polite, clear question or explanation in Ukrainian>",
     "approved_source_text": null
   }}

2. When the user's meaning is 100% clear (either immediately if simple and unambiguous, or once clarified through dialogue):
   Synthesize the final definitive, polished source-language text that accurately conveys all agreed meaning and tone.
   Respond strictly with JSON:
   {{
     "status": "ready",
     "assistant_message": null,
     "approved_source_text": "<The definitive, unambiguous version in {source_lang}>"
   }}

Output strictly valid JSON matching this schema without any markdown wrapping or reasoning.
"""


class AssistantService:
    async def process_turn(
        self,
        conversation_history: List[Dict[str, str]],
        source_lang: str,
        target_lang: str,
        provider_name: str,
        api_key: str,
    ) -> AssistantTurnResult:
        """
        Executes a turn in the assistant intent-clarification dialogue.
        Args:
            conversation_history: List of {"role": "user"|"assistant", "content": "..."}
            source_lang: e.g. "Ukrainian"
            target_lang: e.g. "French"
            provider_name: e.g. "gemini_flash"
            api_key: OpenRouter API key
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

        system_instruction = ASSISTANT_SYSTEM_PROMPT.format(
            source_lang=source_lang,
            target_lang=target_lang,
        )

        messages = [{"role": "system", "content": system_instruction}] + conversation_history

        try:
            response = await client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.2,
                extra_body={"reasoning": {"effort": "none"}},
            )
            raw_content = response.choices[0].message.content or ""
            clean_json = re.sub(r"^```(?:json)?\s*", "", raw_content.strip(), flags=re.IGNORECASE)
            clean_json = re.sub(r"\s*```$", "", clean_json.strip())

            data = json.loads(clean_json)
            status = data.get("status", "ready")
            assist_msg = data.get("assistant_message")
            approved_text = data.get("approved_source_text")

            if status == "clarifying" and assist_msg:
                return AssistantTurnResult(
                    status="clarifying",
                    assistant_message=assist_msg.strip(),
                    approved_source_text=None,
                )
            elif status == "ready":
                return AssistantTurnResult(
                    status="ready",
                    assistant_message=None,
                    approved_source_text=approved_text.strip() if approved_text else None,
                )
        except Exception as e:
            logger.warning(f"Assistant dialogue turn failed: {e}")

        # Fallback: assume ready with original input
        first_user_text = conversation_history[0]["content"] if conversation_history else ""
        return AssistantTurnResult(
            status="ready",
            assistant_message=None,
            approved_source_text=first_user_text,
        )


assistant_service = AssistantService()
