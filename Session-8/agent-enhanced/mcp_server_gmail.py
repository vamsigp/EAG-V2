"""
MCP Server for Gmail Integration
Handles sending emails via Gmail API
"""

import os
import sys
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import logging
from pathlib import Path

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Gmail Configuration
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GMAIL_CREDENTIALS_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # Alternative: OAuth credentials

# Initialize FastMCP
mcp = FastMCP("Gmail")


def get_gmail_service():
    """
    Get Gmail service using either app password or OAuth credentials.
    Returns authenticated Gmail API service.
    """
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.errors import HttpError
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        creds = None
        token_path = Path("token.json")
        
        # Try to load existing token
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            logger.info("Loaded credentials from token.json")
        
        # If no valid credentials, use OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.info("Refreshed expired credentials")
            else:
                # Use credentials file if provided, otherwise use app password
                credentials_file = GMAIL_CREDENTIALS_JSON or "credentials.json"
                
                if Path(credentials_file).exists():
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("Obtained new credentials via OAuth")
                else:
                    # Fall back to app password (SMTP) if no OAuth credentials
                    return None
        
        # Save credentials for next time
        if token_path.exists() or creds:
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('gmail', 'v1', credentials=creds)
        return service
        
    except Exception as e:
        logger.error(f"Error setting up Gmail service: {e}")
        return None


def send_email_smtp(to: str, subject: str, body: str) -> str:
    """
    Send email using SMTP with app password (fallback method).
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        if not GMAIL_USER or not GMAIL_PASSWORD:
            return "Error: GMAIL_USER and GMAIL_PASSWORD must be set for SMTP"
        
        msg = MIMEText(body, 'html')
        msg['From'] = GMAIL_USER
        msg['To'] = to
        msg['Subject'] = subject
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent via SMTP to {to}")
        return f"Email sent successfully to {to}"
        
    except Exception as e:
        logger.error(f"SMTP error: {e}")
        return f"Error sending email via SMTP: {str(e)}"


def create_message(sender: str, to: str, subject: str, body: str) -> dict:
    """Create a message for an email using Gmail API format."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    msg = MIMEText(body, 'html')
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


@mcp.tool()
async def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email via Gmail API.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body (supports HTML)
    
    Returns:
        Success message or error description
    """
    try:
        sender = GMAIL_USER or "me"
        
        # Try Gmail API first
        service = get_gmail_service()
        
        if service:
            try:
                message = create_message(sender, to, subject, body)
                sent_message = service.users().messages().send(
                    userId="me",
                    body=message
                ).execute()
                
                message_id = sent_message.get('id')
                logger.info(f"Email sent via Gmail API. Message ID: {message_id}")
                return f"Email sent successfully to {to}. Message ID: {message_id}"
            except Exception as e:
                logger.warning(f"Gmail API failed, falling back to SMTP: {e}")
        
        # Fall back to SMTP
        return send_email_smtp(to, subject, body)
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting Gmail MCP Server")
    
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for development
    else:
        mcp.run(transport="stdio")  # Run with stdio transport

