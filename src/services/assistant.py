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


ASSISTANT_SYSTEM_PROMPT = """You are an expert bilingual writing and pre-translation assistant.
The user is preparing a message to be translated from {source_lang} to {target_lang}.

CORE CLASSIFICATION RULE (INSTRUCTION VS TRANSLATION):
1. **Instruction to Assistant:**
   - Whenever the user asks you to compose, write, draft, help, adjust tone, add sarcasm, humor, formality, or asks a question (e.g. "напиши...", "склади...", "зроби з підйобом...", "придумай привітання...", "допоможи написати...", "як сказати...", "перефразуй...", "хочу відповісти..."):
     YOU MUST TREAT THIS AS AN ASSISTANCE TASK.
     Draft 2-3 creative, well-tailored text options in Ukrainian with explanations of nuances and tone, and ask the user which version they prefer to translate.
     Respond with:
     {{
       "status": "clarifying",
       "assistant_message": "<Your helpful response, drafted text variants, and tone options in Ukrainian>",
       "approved_source_text": null
     }}

2. **DOUBT BIAS:**
   - If you have ANY doubt whether the user's message is an instruction to you or direct translation text:
     ALWAYS treat it as an instruction/assistance request (`status: "clarifying"`). NEVER translate prompt instructions literally!

3. **Approval for Translation:**
   - Return `status: "ready"` ONLY when:
     a) The user approves a drafted option (e.g. "перекладай 1-й варіант", "так, перекладай", "чудово, відправляй", "підходить", "давай"), OR
     b) The user's input is a completely unambiguous, straightforward declarative message intended directly for the recipient without any prompts, commands, or questions to the assistant.
   - When ready, synthesize the final agreed-upon Ukrainian text in `approved_source_text`:
     {{
       "status": "ready",
       "assistant_message": null,
       "approved_source_text": "<The definitive approved source text in {source_lang}>"
     }}

CRITICAL: Respond ONLY with valid JSON strictly adhering to the schema. No markdown code fences, no extra text.
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
