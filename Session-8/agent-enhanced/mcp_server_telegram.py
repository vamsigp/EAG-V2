"""
MCP Server for Telegram Bot Integration (SSE-based)
Handles receiving messages from Telegram webhooks and sending messages via Telegram Bot API
"""

import os
import sys
import json
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import logging

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SSE_PORT = int(os.getenv("SSE_PORT", "8001"))

# In-memory message queue (in production, use Redis or similar)
message_queue: asyncio.Queue = asyncio.Queue()
last_message: Optional[Dict[str, Any]] = None

# Initialize FastMCP with SSE transport
mcp = FastMCP(
    name="Telegram",
    host="0.0.0.0",
    port=SSE_PORT
)


@mcp.tool()
async def send_telegram_message(chat_id: str, message: str) -> str:
    """
    Send a message to a Telegram chat using the Bot API.
    
    Args:
        chat_id: Telegram chat ID (user ID or group ID)
        message: Message text to send
    
    Returns:
        Success message with message ID
    """
    try:
        import requests
        
        if not TELEGRAM_BOT_TOKEN:
            return "Error: TELEGRAM_BOT_TOKEN not configured"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            msg_id = result.get("result", {}).get("message_id")
            logger.info(f"Message sent to chat {chat_id}, message_id: {msg_id}")
            return f"Message sent successfully. Message ID: {msg_id}"
        else:
            error = result.get("description", "Unknown error")
            logger.error(f"Failed to send message: {error}")
            return f"Failed to send message: {error}"
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_last_message() -> str:
    """
    Get the last message received from Telegram webhook.
    This is used by the agent to retrieve user queries.
    
    Returns:
        Last received message text, or empty string if none
    """
    global last_message
    
    if last_message is None:
        # Try to get from queue if available
        try:
            while not message_queue.empty():
                last_message = message_queue.get_nowait()
        except:
            pass
        
        # Fallback: read from local persistence written by webhook_server
        if last_message is None:
            try:
                # Prefer the file next to this script (same location as webhook_server write)
                base_dir = os.path.dirname(os.path.abspath(__file__))
                read_path = os.path.join(base_dir, "last_message.json")
                with open(read_path, "r", encoding="utf-8") as f:
                    last_message = json.load(f)
                    logger.info(f"Loaded last_message.json from: {read_path}")
            except FileNotFoundError:
                # Fall back to current working directory
                try:
                    with open("last_message.json", "r", encoding="utf-8") as f:
                        last_message = json.load(f)
                        logger.info("Loaded last_message.json from CWD")
                except FileNotFoundError:
                    pass
            except Exception as e:
                logger.warning(f"Could not read last_message.json: {e}")
    
    if last_message:
        message_text = last_message.get("message", {}).get("text", "")
        chat_id = str(last_message.get("message", {}).get("chat", {}).get("id", ""))
        
        result = {
            "text": message_text,
            "chat_id": chat_id,
            "timestamp": last_message.get("message", {}).get("date", "")
        }
        
        logger.info(f"Retrieved last message: {message_text[:50]}...")
        return json.dumps(result, indent=2)
    
    return json.dumps({"text": "", "chat_id": "", "timestamp": ""})


def add_message_to_queue(update: Dict[str, Any]):
    """
    Add a Telegram update to the message queue.
    Called by webhook server when receiving webhook events.
    """
    global last_message
    
    if "message" in update and "text" in update["message"]:
        last_message = update
        try:
            message_queue.put_nowait(update)
            logger.info(f"Message added to queue: {update['message']['text'][:50]}...")
        except Exception as e:
            logger.warning(f"Could not add message to queue: {e}")


if __name__ == "__main__":
    logger.info(f"Starting Telegram MCP Server (SSE) on port {SSE_PORT}")
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        sys.exit(1)
    
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for development
    else:
        mcp.run(transport="sse")  # Run with SSE transport

