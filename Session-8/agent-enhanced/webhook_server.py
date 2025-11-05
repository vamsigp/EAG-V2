"""
Webhook Server for Telegram Bot
Receives webhook events from Telegram and forwards them to Telegram MCP Server
"""

import os
import sys
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import requests

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")  # Public URL for webhook
TELEGRAM_MCP_SERVER_URL = os.getenv("TELEGRAM_MCP_SERVER_URL", "http://localhost:8001")

app = FastAPI(title="Telegram Webhook Server")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "telegram-webhook-server"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Receives webhook events from Telegram.
    Forwards messages to Telegram MCP Server via HTTP or stores locally.
    """
    try:
        data = await request.json()
        logger.info(f"Received webhook update: {json.dumps(data, indent=2)[:200]}...")
        
        # Check if it's a message update
        if "message" in data and "text" in data["message"]:
            message_text = data["message"]["text"]
            chat_id = data["message"]["chat"]["id"]
            
            logger.info(f"Processing message from chat {chat_id}: {message_text[:50]}...")
            
            # Persist last message locally so the MCP server/agent can read it
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                save_path = os.path.join(base_dir, "last_message.json")
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved last_message.json at: {save_path}")
            except Exception as e:
                logger.warning(f"Could not save last_message.json: {e}")
            
            # Forward to Telegram MCP Server via HTTP POST
            # The MCP server will expose an endpoint to receive this
            try:
                forward_url = f"{TELEGRAM_MCP_SERVER_URL}/receive_message"
                response = requests.post(
                    forward_url,
                    json=data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info("Message forwarded to MCP server successfully")
                else:
                    logger.warning(f"MCP server returned status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Could not forward to MCP server: {e}")
                # Continue anyway - message will be retrieved via get_last_message tool
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def setup_telegram_webhook():
    """
    Configure Telegram to send webhooks to this server.
    Call this after starting the webhook server.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Cannot setup webhook.")
        return False
    
    if not TELEGRAM_WEBHOOK_URL:
        logger.warning("TELEGRAM_WEBHOOK_URL not set. Webhook will not be configured automatically.")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
        payload = {
            "url": f"{TELEGRAM_WEBHOOK_URL}/webhook"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            logger.info(f"Webhook configured: {TELEGRAM_WEBHOOK_URL}/webhook")
            return True
        else:
            logger.error(f"Failed to setup webhook: {result.get('description')}")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up webhook: {e}")
        return False


if __name__ == "__main__":
    logger.info(f"Starting Telegram Webhook Server on port {WEBHOOK_PORT}")
    
    # Setup webhook if URL is provided
    if TELEGRAM_WEBHOOK_URL:
        setup_telegram_webhook()
    else:
        logger.warning("=" * 60)
        logger.warning("⚠️  TELEGRAM_WEBHOOK_URL not set!")
        logger.warning("=" * 60)
        logger.warning("To set up a local webhook URL:")
        logger.warning("1. Use cloudflared (no signup): cloudflared tunnel --url http://localhost:8080")
        logger.warning("2. Use ngrok: ngrok http 8080")
        logger.warning("3. Run helper script: python setup_webhook_tunnel.py")
        logger.warning("")
        logger.warning("See WEBHOOK_SETUP.md for detailed instructions.")
        logger.warning("=" * 60)
        logger.info("Server running without webhook. Telegram will use polling or manual getUpdates.")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=WEBHOOK_PORT,
        log_level="info"
    )

