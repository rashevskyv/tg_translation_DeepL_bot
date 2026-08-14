# Telegram Translation Bot (DeepL & Multi-LLM)

A modern, high-performance, asynchronous Telegram bot for automated bidirectional translations between **Ukrainian** and any foreign language with support for 5 translation engines: **DeepL**, **OpenAI**, **Google Gemini**, **Qwen**, and **DeepSeek**.

---

## 🌟 Key Features

- **Smart Bidirectional Translation:**
  - **Ukrainian text** $\rightarrow$ Automatically translated into your configured **Target Language** (e.g. English, German, Polish, Spanish, etc.).
  - **Foreign text (non-Ukrainian)** $\rightarrow$ Language is automatically detected and translated into **Ukrainian**.
- **Multi-Engine Support:**
  - 🔵 **DeepL:** Industry-standard neural machine translation (supports both Free `:fx` and Pro keys).
  - 🟢 **OpenAI:** Fast, contextual translation powered by `gpt-4o-mini`.
  - 🔴 **Google Gemini:** Ultra-fast streaming translations powered by `gemini-2.0-flash`.
  - 🟣 **Qwen:** Alibaba Cloud DashScope `qwen-plus` model.
  - 🔷 **DeepSeek:** High precision `deepseek-chat` model.
- **Real-Time Streaming & One-Click Copy:**
  - For LLM providers, translations stream directly to the chat with throttled updates to respect Telegram rate limits.
  - Once translation completes, the intermediate stream message is deleted, and the final translation is delivered in a code block (`<pre><code>`), enabling **instant one-click copy to clipboard**.
- **Interactive In-Chat Settings GUI (`/settings`):**
  - **Set Target Language:** Click the button and type your target language (e.g., `English`, `German`, `pl`, `es`).
  - **Switch Active Engine:** Choose any supported provider via inline buttons.
  - **Manage API Keys:** Set, view (masked), or delete personal API keys directly inside the chat.
- **Privacy & Security:**
  - Sensitive messages containing API keys are **immediately deleted** from the chat after saving.
  - API keys and user preferences are stored per-user in a local SQLite database (`users.db`).
  - Strict `.gitignore` ensures no secrets or database files are committed to Git.

---

## 📋 Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Launch the bot, view welcome instructions, and inspect current settings |
| `/settings` | Open interactive settings menu (target language, active engine, API keys) |
| `/help` | Display usage guide and supported engine details |

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

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
nano .env
```

Fill in your `BOT_TOKEN` and any optional fallback API keys:

```ini
# Required:
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ

# Optional Server-Wide Fallback Keys:
DEEPL_API_KEY=7d501876-f8ec-481c-9795-7fc2396a7e22:fx
OPENAI_API_KEY=
GEMINI_API_KEY=
DASHSCOPE_API_KEY=
DEEPSEEK_API_KEY=

# Settings
DEFAULT_TARGET_LANGUAGE=English
DEFAULT_PROVIDER=deepl
DATABASE_PATH=data/translator.db
LOG_LEVEL=INFO
```

### 3. Install & Start as Systemd Service

Copy the service file into systemd:

```bash
sudo cp systemd/tg-translator.service /etc/systemd/system/tg-translator.service

# Reload daemon and enable service
sudo systemctl daemon-reload
sudo systemctl enable tg-translator.service
sudo systemctl start tg-translator.service
```

### 4. Monitor & Check Logs

```bash
# Check status
sudo systemctl status tg-translator.service

# View real-time logs
journalctl -u tg-translator.service -f
```

---

## 🧪 Running Tests (Parallel Execution)

Run all unit and integration tests in parallel using `pytest-xdist`:

```powershell
pytest -n auto -v
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` or `*.db` files.** They are ignored in `.gitignore`.
2. **Per-User Keys:** Each user can securely provide their own API key via `/settings`, avoiding centralized API quota depletion.
3. **Auto-Deletion:** The bot automatically removes messages containing API keys right after they are entered.
