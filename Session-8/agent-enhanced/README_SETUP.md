# Enhanced Agent Setup Guide

This guide will help you set up the enhanced agent with Telegram, Gmail, and Google Drive integration.

## Prerequisites

1. **Python 3.11+**
2. **Telegram Bot Token** (from BotFather)
3. **Gmail App Password** or OAuth credentials
4. **Google Cloud Service Account** JSON file
5. **Gemini API Key**

## Step 1: Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in all the required values:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `GMAIL_USER`: Your Gmail address
   - `GMAIL_PASSWORD`: Your Gmail app password
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: Path to your Google service account JSON file (or use base64)
   - `GEMINI_API_KEY`: Your Gemini API key

## Step 2: Install Dependencies

```bash
uv sync
# or
pip install -r requirements.txt  # if you create one
```

## Step 3: Google Cloud Setup

### Enable APIs
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API
   - Gmail API

### Create Service Account
1. Navigate to IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name it (e.g., "agent-service")
4. Grant it the following roles:
   - Editor (or more specific: Service Account User, Sheets Editor, Drive Editor)
5. Click "Create and Download JSON"
6. Save the JSON file as `credentials_sa.json` in the project root

### Gmail API Setup (Choose One Method)

**Method 1: App Password (Simpler)**
1. Enable 2FA on your Google account
2. Go to Google Account → Security → App passwords
3. Generate a new app password
4. Copy it to `GMAIL_PASSWORD` in `.env`

**Method 2: OAuth (More Secure)**
1. Follow [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python)
2. Download `credentials.json`
3. Run the setup once to generate `token.json`
4. Set `GOOGLE_SERVICE_ACCOUNT_JSON=credentials.json` in `.env`

## Step 4: Telegram Bot Setup

### Get Bot Token
1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow instructions
3. Save the token to `TELEGRAM_BOT_TOKEN` in `.env`

### Get Your Chat ID
1. Start a chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find your chat ID in the response

### Configure Webhook (Optional - for production)
For local development, use ngrok:
```bash
ngrok http 8080
```
Then set `TELEGRAM_WEBHOOK_URL` to your ngrok URL in `.env`

## Step 5: Place Credential Files

Place the following files in the project root:
- `credentials_sa.json` - Google Service Account credentials
- `token.json` - Gmail OAuth token (if using OAuth method)

## Step 6: Running the Servers

### Terminal 1: Start Telegram MCP Server (SSE)
```bash
cd agent-enhanced
python mcp_server_telegram.py
```
This starts the SSE server on port 8001.

### Terminal 2: Start Webhook Server (Optional - for receiving messages)
```bash
cd agent-enhanced
python webhook_server.py
```
This starts the webhook server on port 8080.

### Terminal 3: Run the Agent
```bash
cd agent-enhanced
python agent.py
```

## Step 7: Testing the Workflow

1. Send a message to your Telegram bot: "Find the Current Point Standings of F1 Racers"
2. The agent will:
   - Retrieve the message via `get_last_message` tool
   - Search for F1 standings using web search
   - Create a Google Sheet with the data
   - Get the shareable link
   - Send the link to your email via Gmail

## Troubleshooting

### Telegram Bot Not Responding
- Check if `TELEGRAM_BOT_TOKEN` is correct
- Ensure the bot is running and accessible
- Verify webhook is configured (for production)

### Gmail Not Sending
- Verify `GMAIL_USER` and `GMAIL_PASSWORD` are correct
- If using OAuth, ensure `token.json` exists and is valid
- Check Google Account security settings

### Google Sheets Not Creating
- Verify `credentials_sa.json` is in the project root
- Ensure Google Sheets and Drive APIs are enabled
- Check service account has proper permissions

### SSE Connection Failed
- Ensure Telegram MCP server is running on port 8001
- Check firewall settings
- Verify `SSE_PORT` matches in `.env` and `profiles.yaml`

## File Structure

```
agent-enhanced/
├── agent.py                 # Main agent entry point
├── mcp_server_telegram.py   # Telegram MCP server (SSE)
├── mcp_server_gmail.py      # Gmail MCP server (stdio)
├── mcp_server_gdrive.py     # Google Drive MCP server (stdio)
├── webhook_server.py        # Telegram webhook receiver
├── core/                    # Core agent logic
├── modules/                  # Agent modules
├── config/                   # Configuration files
├── credentials_sa.json       # Google Service Account (place here)
├── token.json               # Gmail OAuth token (if using)
└── .env                     # Environment variables (create from .env.example)
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from BotFather |
| `GMAIL_USER` | Yes | Your Gmail address |
| `GMAIL_PASSWORD` | Yes* | Gmail app password (if using SMTP) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Yes | Path to Google service account JSON |
| `GEMINI_API_KEY` | Yes | Gemini API key |
| `SSE_PORT` | No | Port for SSE server (default: 8001) |
| `WEBHOOK_PORT` | No | Port for webhook server (default: 8080) |
| `TELEGRAM_WEBHOOK_URL` | No | Public URL for webhook (for production) |

## Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

