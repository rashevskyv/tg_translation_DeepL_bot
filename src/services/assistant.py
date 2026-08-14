import json
import logging
import re
from typing import Dict, List, NamedTuple, Optional
from openai import AsyncOpenAI
from src.config import PROVIDERS_INFO

logger = logging.getLogger(__name__)


class AssistantTurnResult(NamedTuple):
    status: str  # "ready" (approved for translation) or "clarifying" (needs more conversation)
    assistant_message: Optional[str]  # Question, drafting suggestions, or reply to the user in Ukrainian
    approved_source_text: Optional[str]  # Final agreed-upon source text to send to translator engine


ASSISTANT_SYSTEM_PROMPT = """You are an expert conversational pre-translation and copywriting assistant.
The user is preparing a message or text to be translated from {source_lang} to {target_lang}.

YOUR CAPABILITIES AND RESPONSIBILITIES:
1. **Collaborative Writing & Drafting:**
   - Help the user compose, rephrase, expand, or adjust the emotional coloring and tone of any text (e.g. formal, friendly, polite, sarcastic, humorous, business, diplomatic, persuasive).
   - If the user asks for help like "допоможи написати листа", "зроби це більш ввічливим", "підбери краще формулювання", "напиши привітання", propose options and discuss ideas in Ukrainian.
2. **Ambiguity & Nuance Clarification:**
   - If the user provides a message with double meanings, slang, vague context, or multiple styles, ask clarifying questions in Ukrainian.
3. **Dialogue & Memory Awareness:**
   - You have access to the full conversation history. Keep context across turns naturally.
4. **Final Approval & Translation Trigger:**
   - When the text is fully agreed upon, perfected, and approved by the user (e.g., the user says "так, перекладай", "чудово", "підходить", "давай", or when simple input was already 100% crystal-clear without needing changes):
     Synthesize the definitive, high-quality message in {source_lang} to be translated.
     Respond with JSON:
     {{
       "status": "ready",
       "assistant_message": null,
       "approved_source_text": "<The definitive, approved text in {source_lang}>"
     }}
   - If you are still discussing, proposing drafts, asking questions, or awaiting user feedback:
     Respond with JSON:
     {{
       "status": "clarifying",
       "assistant_message": "<Your helpful response, drafted text options, or questions in Ukrainian>",
       "approved_source_text": null
     }}

CRITICAL: Respond ONLY with valid JSON strictly adhering to the schema above. No markdown code blocks, no extraneous text.
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
        Executes a turn in the assistant intent-clarification and collaborative writing dialogue.
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
                temperature=0.3,
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
            logger.warning(f"Assistant dialogue turn error: {e}")

        # Fallback
        last_user_text = next((m["content"] for m in reversed(conversation_history) if m["role"] == "user"), "")
        return AssistantTurnResult(
            status="ready",
            assistant_message=None,
            approved_source_text=last_user_text,
        )


assistant_service = AssistantService()
