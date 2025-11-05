# Local Webhook Setup Guide

This guide explains how to set up a local webhook URL so Telegram can send messages to your local development server.

## Why You Need a Webhook URL

Telegram needs a **public HTTPS URL** to send webhook events to your bot. Since your local server (`localhost:8080`) is not publicly accessible, you need a tunnel service to create a public URL that forwards requests to your local server.

## Quick Start: Choose Your Method

### Method 1: cloudflared (Recommended - No Signup Required) ⭐

**Advantages:**
- Free, no account needed
- Official Cloudflare service
- Works out of the box

**Steps:**
1. Install cloudflared:
   - **Windows**: Download from [releases](https://github.com/cloudflare/cloudflared/releases) or use:
     ```powershell
     winget install --id Cloudflare.cloudflared
     ```
   - **macOS**: `brew install cloudflared`
   - **Linux**: Download from [releases](https://github.com/cloudflare/cloudflared/releases)

2. Start your webhook server (in Terminal 1):
   ```bash
   python webhook_server.py
   ```

3. Start cloudflared tunnel (in Terminal 2):
   ```bash
   cloudflared tunnel --url http://localhost:8080
   ```

4. Copy the HTTPS URL shown (e.g., `https://xxxx.trycloudflare.com`)

5. Add to your `.env` file:
   ```
   TELEGRAM_WEBHOOK_URL=https://xxxx.trycloudflare.com
   ```

6. Restart `webhook_server.py` - it will automatically configure the webhook with Telegram!

### Method 2: ngrok (Stable but Requires Signup)

**Advantages:**
- Very stable
- Free tier available
- Persistent URLs with paid plans

**Steps:**
1. Sign up at [ngrok.com](https://ngrok.com) (free account)
2. Download and install ngrok
3. Authenticate (run once):
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

4. Start your webhook server (Terminal 1):
   ```bash
   python webhook_server.py
   ```

5. Start ngrok (Terminal 2):
   ```bash
   ngrok http 8080
   ```

6. Copy the HTTPS URL from ngrok (e.g., `https://xxxx.ngrok.io`)

7. Add to `.env`:
   ```
   TELEGRAM_WEBHOOK_URL=https://xxxx.ngrok.io
   ```

8. Restart `webhook_server.py`

### Method 3: Using the Helper Script

We've created a helper script that can guide you through the setup:

```bash
python setup_webhook_tunnel.py
```

This script will:
- Check if your webhook server is running
- Guide you through setting up ngrok or cloudflared
- Help configure the webhook with Telegram

## Step-by-Step Process

1. **Start the webhook server:**
   ```bash
   python webhook_server.py
   ```
   You should see: `Starting Telegram Webhook Server on port 8080`

2. **Set up a tunnel** (choose one method above)

3. **Update your `.env` file:**
   ```
   TELEGRAM_WEBHOOK_URL=https://your-tunnel-url
   ```

4. **Restart the webhook server** - it will automatically call Telegram's API to set up the webhook

5. **Verify webhook is working:**
   Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo`
   You should see your webhook URL in the response

## Testing

1. Send a message to your Telegram bot
2. Check the webhook server logs - you should see:
   ```
   Received webhook update: ...
   Processing message from chat ...
   ```

## Troubleshooting

### Webhook URL Not Working
- Make sure the tunnel is running (don't close the terminal)
- Verify the URL in `.env` matches exactly (including `https://`)
- Check that port 8080 matches `WEBHOOK_PORT` in `.env`

### Telegram Says Webhook Failed
- Ensure your webhook server is running
- Check that the tunnel is active
- Verify the URL format: `https://domain.com/webhook` (no trailing slash)

### Messages Not Received
- Check webhook server logs for errors
- Verify the tunnel URL is still active (they can expire)
- Make sure `TELEGRAM_MCP_SERVER_URL` points to your MCP server (default: `http://localhost:8001`)

## Alternative: Polling Mode (No Webhook Needed)

If you don't want to use webhooks, you can use polling instead. However, this requires modifying the code to use the Telegram Bot API's `getUpdates` method. The current setup is optimized for webhooks.

## Important Notes

- **Tunnel URLs change**: Free tunnel services (cloudflared, ngrok free tier) generate new URLs each time. Update your `.env` if you restart the tunnel.
- **Keep tunnel running**: The tunnel must stay running while developing. Close it when done.
- **HTTPS required**: Telegram only accepts HTTPS URLs for webhooks.

## Next Steps

After setting up the webhook:
1. Start your Telegram MCP server: `python mcp_server_telegram.py`
2. Start your agent: `python agent.py`
3. Test by sending a message to your bot!

