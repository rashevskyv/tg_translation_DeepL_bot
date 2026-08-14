# Telegram Translation Bot (DeepL & OpenRouter LLMs)

A modern, high-performance, asynchronous Telegram bot for automated bidirectional translations between **Ukrainian** and any foreign language with support for **DeepL Standalone**, top-tier LLMs via **OpenRouter** (`Gemini 3.5 Flash Lite`, `Gemini 3.7 Flash`, `GPT-5.6 Luna`, `DeepSeek V4 Flash`) running in **Non-Thinking mode**, and an **Intelligent Assistant Mode** with context clarification.

---

## 🌟 Key Features

- **Smart Bidirectional Translation:**
  - **Ukrainian text** $\rightarrow$ Automatically translated into your configured **Target Language** (e.g. Portuguese, English, German, Polish, Spanish, etc.).
  - **Foreign text (non-Ukrainian)** $\rightarrow$ Language is automatically detected and translated into **Ukrainian**.
- **Translation Modes:**
  - **⚡ Direct Translation:** Fast, instant, clean translation wrapped in copyable `<code>...</code>` format without interruptions.
  - **💡 Assistant Mode:** Analyzes message intent and nuances. If ambiguous or tone is unclear, asks clarifying questions in Ukrainian first before delivering a polished, perfectly styled translation.
- **Independent Engine Configurations:**
  - 🔵 **Translator Engine:** DeepL (Standalone), Gemini 3.5 Flash Lite, Gemini 3.7 Flash, GPT-5.6 Luna, DeepSeek V4 Flash.
  - 🧠 **Assistant Engine:** Independent LLM selection for intent analysis (e.g., Gemini 3.7 Flash or GPT-5.6 Luna).
- **Conversational Target Language Extraction:**
  - Type any full sentence or utterance (e.g. *"хочу перекладати на португальську, європейський варіант"*), and **DeepSeek V4 Flash** instantly extracts the target language and maps it to official DeepL API codes.
- **Enforced Non-Thinking Mode:**
  - All LLM models operate in pure translation mode without reasoning artifacts or thought delays (`reasoning: {"effort": "none"}`).
- **Interactive In-Chat Settings GUI (`/settings`):**
  - Change target language, toggle translation modes, switch translator/assistant models, and manage API keys privately.

---

## 🔄 How to Update on Server

To update the bot on your Ubuntu server to the latest version:

```bash
cd ~/tg_translation_DeepL_bot
git pull origin main
systemctl restart tg-translator.service
systemctl status tg-translator.service --no-pager
```

---

## 🔑 How to Register & Get OpenRouter API Keys

OpenRouter is a unified platform providing access to hundreds of AI models via a single API key:

1. **Sign Up:**
   - Go to [openrouter.ai](https://openrouter.ai) and create an account (using Google, GitHub, or email).
2. **Add Credits:**
   - Navigate to [openrouter.ai/credits](https://openrouter.ai/credits) to add a balance (supports cards, crypto).
3. **Create an API Key:**
   - Go to [openrouter.ai/keys](https://openrouter.ai/keys).
   - Click **Create Key**, give it a name (e.g., `Telegram Bot`), and copy the generated key (starts with `sk-or-v1-...`).
4. **Add to Bot:**
   - Either paste it in your `.env` file as `OPENROUTER_API_KEY=sk-or-v1-...`
   - Or open the bot, tap **⚙️ Settings** $\rightarrow$ **🔑 Manage API Keys** $\rightarrow$ **OpenRouter API Key** $\rightarrow$ **✏️ Enter / Replace API Key** and send it.

---

## 📋 Bot Commands & Controls

| Trigger | Description |
| :--- | :--- |
| `/start` | Launch the bot, view welcome instructions, and inspect current settings |
| `/settings` or `⚙️ Settings` | Open interactive settings menu (target language, mode, engines, API keys) |
| `/help` or `ℹ️ Help` | Display usage guide, modes, and engine details |
| `[ Menu ]` Button | Native Telegram menu button in bottom-left corner |
| `/assign_key <uid> <prov> <key>` | *(Admin only)* Assign specific API key to a user ID |
| `/user_info <uid>` | *(Admin only)* Inspect user's current settings and custom keys |

---

## 🛠️ User & Key Management CLI Tool

Admins can manage user preferences and API keys directly from the terminal:

```bash
# 1. List all registered users
python -m src.tools.manage_user list

# 2. Assign custom API key to a specific user
python -m src.tools.manage_user set-key --user-id 123456789 --provider openrouter --key sk-or-v1-...

# 3. Delete user's custom key
python -m src.tools.manage_user delete-key --user-id 123456789 --provider openrouter

# 4. Update user's settings (language / model / mode)
python -m src.tools.manage_user set-settings --user-id 123456789 --target-lang Portuguese --provider gemini_flash
```

---

## 🧪 Running Tests (Parallel Execution)

```powershell
pytest -n auto -v
```
