# Quick Start Guide

## 🚀 Quick Setup Steps

### 1. Copy Environment Template
```bash
# Create .env file from example
cp .env.example .env
# Edit .env with your credentials
```

### 2. Place Credential Files
Place your `credentials_sa.json` file in the `agent-enhanced/` directory.

### 3. Install Dependencies
```bash
cd agent-enhanced
uv sync
# or
pip install -r requirements.txt
```

### 4. Start Services

**Terminal 1 - Telegram MCP Server (SSE):**
```bash
cd agent-enhanced
python mcp_server_telegram.py
```

**Terminal 2 - Webhook Server (Optional - for receiving messages):**
```bash
cd agent-enhanced
python webhook_server.py
```

**Terminal 3 - Run Agent:**
```bash
cd agent-enhanced
python agent.py
```

## 📋 Environment Variables Checklist

Make sure these are set in your `.env` file:

- ✅ `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- ✅ `GMAIL_USER` - Your Gmail address  
- ✅ `GMAIL_PASSWORD` - Gmail app password
- ✅ `GOOGLE_SERVICE_ACCOUNT_JSON` - Path to credentials_sa.json
- ✅ `GEMINI_API_KEY` - Your Gemini API key

## 🔄 Workflow Test

1. Send message to Telegram bot: **"Find the Current Point Standings of F1 Racers"**
2. Agent will:
   - Get message via `get_last_message` tool
   - Search web for F1 standings
   - Create Google Sheet with data
   - Get shareable link
   - Email link to you via Gmail

## 📁 Required Files

- `credentials_sa.json` - Google Service Account JSON (place in root)
- `token.json` - Gmail OAuth token (auto-generated if using OAuth)

## 🐛 Troubleshooting

See `README_SETUP.md` for detailed troubleshooting guide.

