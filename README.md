# Telegram Translation Bot (DeepL & OpenRouter LLMs)

A modern, high-performance, asynchronous Telegram bot for automated bidirectional translations between **Ukrainian** and any foreign language with support for **DeepL Standalone** and top-tier LLMs via **OpenRouter** (`Gemini 3.5 Flash Lite`, `Gemini 3.7 Flash`, `GPT-5.6 Luna`, `DeepSeek V4 Flash`) running in **Non-Thinking mode**.

---

## 🌟 Key Features

- **Smart Bidirectional Translation:**
  - **Ukrainian text** $\rightarrow$ Automatically translated into your configured **Target Language** (e.g. Portuguese, English, German, Polish, Spanish, etc.).
  - **Foreign text (non-Ukrainian)** $\rightarrow$ Language is automatically detected and translated into **Ukrainian**.
- **Supported Translation Engines:**
  - 🔵 **DeepL (Standalone):** Industry-standard neural machine translation (supports Free `:fx` and Pro keys).
  - 🔴 **Gemini 3.5 Flash Lite (OpenRouter):** Ultra-fast, low-latency translation (`google/gemini-3.5-flash-lite`).
  - 🔴 **Gemini 3.7 Flash (OpenRouter):** Next-gen multimodal translation (`google/gemini-3.7-flash`).
  - 🟢 **OpenAI GPT-5.6 Luna (OpenRouter):** State-of-the-art language intelligence (`openai/gpt-5.6-luna`).
  - 🔷 **DeepSeek V4 Flash (OpenRouter):** High efficiency translation (`deepseek/deepseek-v4-flash-0731`).
- **Enforced Non-Thinking Mode:**
  - All LLM models operate in pure translation mode without reasoning artifacts or thought delays (`reasoning: {"effort": "none"}`).
- **Real-Time Streaming & One-Click Tap-to-Copy:**
  - Fast token streaming with throttled updates.
  - Final translation delivered inside `<code>...</code>` tags — **single click/tap copies immediately to clipboard**.
- **Interactive In-Chat Settings GUI (`/settings`):**
  - **Multilingual Target Language Input:** Type the target language in Ukrainian, English, or ISO code (e.g., `Португальська`, `Portuguese`, `pt`).
  - **Switch Active Engine:** Pick between DeepL and any OpenRouter model.
  - **Manage API Keys:** Set your standalone DeepL key and a single universal **OpenRouter API Key** (covers all 4 LLM models).

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
| `/settings` or `⚙️ Settings` | Open interactive settings menu (target language, active engine, API keys) |
| `/help` or `ℹ️ Help` | Display usage guide and supported engine details |
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

# 4. Update user's settings (language / model)
python -m src.tools.manage_user set-settings --user-id 123456789 --target-lang Portuguese --provider gemini_flash
```

---

## 🚀 Deployment Guide (Ubuntu Linux / Systemd)

### 1. Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/your-username/tg_translation_DeepL_bot.git /opt/tg_translation_DeepL_bot
cd /opt/tg_translation_DeepL_bot

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

```ini
# Required:
BOT_TOKEN=8607012156:AAFfPNVHrFQ7SaCMJsae_0pW8tXKjaKrA28

# Provider API Keys:
DEEPL_API_KEY=7d501876-f8ec-481c-9795-7fc2396a7e22:fx
OPENROUTER_API_KEY=sk-or-v1-your_openrouter_key_here

# Settings
DEFAULT_TARGET_LANGUAGE=English
DEFAULT_PROVIDER=deepl
DATABASE_PATH=data/translator.db
LOG_LEVEL=INFO
```

### 3. Install & Start as Systemd Service

```bash
sudo cp systemd/tg-translator.service /etc/systemd/system/tg-translator.service

sudo systemctl daemon-reload
sudo systemctl enable --now tg-translator.service
```

---

## 🧪 Running Tests (Parallel Execution)

```powershell
pytest -n auto -v
```
