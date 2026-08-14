#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🚀 Installing Telegram Translation Bot..."
echo "=========================================="

APP_DIR="$HOME/tg_translation_DeepL_bot"

# 1. Clean broken repositories & install dependencies
rm -f /etc/apt/sources.list.d/*speedtest* /etc/apt/sources.list.d/*ookla* 2>/dev/null || true
apt update -y || true
apt install -y git python3 python3-pip python3-venv

# 2. Clone or update repository
if [ -d "$APP_DIR" ]; then
    echo "🔄 Updating repository at $APP_DIR..."
    cd "$APP_DIR"
    git pull origin main
else
    echo "📥 Cloning repository into $APP_DIR..."
    git clone https://github.com/rashevskyv/tg_translation_DeepL_bot.git "$APP_DIR"
    cd "$APP_DIR"
fi

# 3. Setup venv & dependencies
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Write .env if provided or from defaults
echo "⚙️ Configuring .env file..."
cat << EOF > "$APP_DIR/.env"
BOT_TOKEN=${BOT_TOKEN:-}
DEEPL_API_KEY=${DEEPL_API_KEY:-}
OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
OPENAI_API_KEY=${OPENAI_API_KEY:-}
ADMIN_USER_IDS=${ADMIN_USER_IDS:-}
DEFAULT_TARGET_LANGUAGE=${DEFAULT_TARGET_LANGUAGE:-English}
DEFAULT_PROVIDER=${DEFAULT_PROVIDER:-deepl}
DATABASE_PATH=data/translator.db
LOG_LEVEL=INFO
EOF

# 5. Initialize user keys in SQLite if provided
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "🔑 Initializing user OpenRouter keys..."
    ./venv/bin/python -m src.tools.manage_user set-key --user-id 252419732 --provider openrouter --key "$OPENROUTER_API_KEY" 2>/dev/null || true
    ./venv/bin/python -m src.tools.manage_user set-key --user-id 5301883186 --provider openrouter --key "$OPENROUTER_API_KEY" 2>/dev/null || true
fi

# 6. Install systemd service
echo "⚙️ Creating systemd service..."
cat << EOF > /etc/systemd/system/tg-translator.service
[Unit]
Description=Telegram Multi-Engine Translation Bot
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python -m src.main
Restart=always
RestartSec=5s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tg-translator-bot

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now tg-translator.service

echo "=========================================="
echo "✅ Bot installed & started successfully!"
echo "=========================================="
systemctl status tg-translator.service --no-pager
