#!/usr/bin/env bash
set -e

APP_DIR="$HOME/tg_translation_DeepL_bot"

echo "========================================="
echo "🚀 Deploying Telegram Translation Bot..."
echo "========================================="

# 1. Update and install packages
echo "📦 Installing system dependencies..."
apt update -y && apt install -y git python3 python3-pip python3-venv

# 2. Clone or update repository
if [ -d "$APP_DIR" ]; then
    echo "🔄 Updating existing repository at $APP_DIR..."
    cd "$APP_DIR"
    git pull origin main
else
    echo "📥 Cloning repository into $APP_DIR..."
    git clone https://github.com/rashevskyv/tg_translation_DeepL_bot.git "$APP_DIR"
    cd "$APP_DIR"
fi

# 3. Create virtual environment & install requirements
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Create .env from template if not exists
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚙️ Creating .env configuration from .env.example..."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
fi

# 5. Configure systemd service
echo "⚙️ Configuring systemd service..."
cat <<EOF > /etc/systemd/system/tg-translator.service
[Unit]
Description=Telegram Multi-Engine Translation Bot
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
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

echo "========================================="
echo "✅ Deployment completed successfully!"
echo "========================================="
systemctl status tg-translator.service --no-pager
