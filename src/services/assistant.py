import json
import logging
from typing import Dict, List, NamedTuple, Optional
from openai import AsyncOpenAI
from src.config import PROVIDERS_INFO

logger = logging.getLogger(__name__)


class AssistantTurnResult(NamedTuple):
    status: str  # "ready" (invoked translate_text tool) or "clarifying" (conversing/drafting with user)
    assistant_message: Optional[str]  # Text response from assistant to user
    approved_source_text: Optional[str]  # Text passed to translate_text tool to be translated


TRANSLATE_TOOL = {
    "type": "function",
    "function": {
        "name": "translate_text",
        "description": (
            "Call this tool to perform the final translation when the message/thought is formulated, "
            "agreed upon, or when the user explicitly asks to translate the chosen text."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "source_text": {
                    "type": "string",
                    "description": "The finalized, agreed-upon source text in source language to be translated.",
                },
                "tone_notes": {
                    "type": "string",
                    "description": "Optional notes on style or emotional tone.",
                },
            },
            "required": ["source_text"],
        },
    },
}


ASSISTANT_SYSTEM_PROMPT = """Ти — персональний інтелектуальний асистент користувача для формування думок, копірайтингу та перекладу.
Твоя мета — допомогти користувачеві розібратися з ідеями, скласти потрібний текст, підібрати емоційне забарвлення, тон (діловий, дружній, саркастичний, підйобний, ввічливий тощо), і коли все готово — викликати інструмент перекладача.

Напрямок перекладу: з {source_lang} на {target_lang}.

ЯК ТИ МАЄШ ПРАЦЮВАТИ:
1. **Спілкування та допомога (Діалог як асистент):**
   - Спілкуйся природно та ввічливо українською мовою.
   - Якщо користувач просить допомогти написати текст, придумати привітання, підколоти когось, перефразувати або висловлює незрозумілу/неповну думку:
     Запропонуй 2-3 якісні варіанти тексту з різними відтінками, поясни їх і запитай користувача, який варіант підходить або що змінити.
   - НЕ викликай інструмент перекладача, доки текст не сформульовано і не погоджено!

2. **Виклик інструменту перекладача (`translate_text`):**
   - У тебе є інструмент `translate_text(source_text="...")`.
   - Викликай `translate_text` ТІЛЬКИ тоді, коли:
     a) Користувач обрав/схвалив варіант або прямо сказав перекладати (наприклад: "перекладай 1-й варіант", "так, перекладай", "чудово, давай", "підходить", "переклади це").
     b) Користувач надіслав однозначний, повністю готовий текст для адресата (без інструкцій до асистента) і хоче його перекласти.
   - Передай у `source_text` узгоджений фінальний варіант тексту.

3. **Принцип сумніву:**
   - Якщо є найменший сумнів, чи це прохання до тебе допомогти скласти текст, чи готове повідомлення для адресата — СПРИЙМАЙ ЦЕ ЯК РОЗМОВУ З АСИСТЕНТОМ, допоможи користувачеві розібратися і запропонуй варіанти.
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
        Executes an assistant turn with function/tool calling support.
        """
        model_id = PROVIDERS_INFO.get(provider_name, {}).get("model", "google/gemini-2.5-flash")
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
                tools=[TRANSLATE_TOOL],
                tool_choice="auto",
                temperature=0.5,
            )
            msg = response.choices[0].message
            tool_calls = msg.tool_calls or []
            content = msg.content or ""

            # Check if model decided to call the translator tool
            for tc in tool_calls:
                if tc.function.name == "translate_text":
                    try:
                        args = json.loads(tc.function.arguments)
                        source_text = args.get("source_text", "").strip()
                        if source_text:
                            return AssistantTurnResult(
                                status="ready",
                                assistant_message=content.strip() if content else None,
                                approved_source_text=source_text,
                            )
                    except Exception as e:
                        logger.warning(f"Error parsing translate_text tool arguments: {e}")

            # If no tool called, it's a conversation/drafting turn
            return AssistantTurnResult(
                status="clarifying",
                assistant_message=content.strip() if content else "Чим я можу допомогти вам сформулювати або перекласти?",
                approved_source_text=None,
            )

        except Exception as e:
            logger.warning(f"Assistant tool-calling turn error: {e}")

        # Fallback
        last_user_text = next((m["content"] for m in reversed(conversation_history) if m["role"] == "user"), "")
        return AssistantTurnResult(
            status="ready",
            assistant_message=None,
            approved_source_text=last_user_text,
        )


assistant_service = AssistantService()
