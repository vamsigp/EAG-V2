# MCP Paint Automation

This project demonstrates controlling Microsoft Paint via an MCP server and a Gemini-powered agent. The agent connects to the MCP server (`functions.py`) and calls tools to open Paint, draw a rectangle, and insert text.

## Prerequisites
- Windows 10/11
- Python 3.10+
- Microsoft Paint installed (default on Windows)
- A Google Gemini API key

## Setup
1. Create and populate a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
# For email sending
GMAIL_USER=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
# Where to send the email (optional if you pass 'to' explicitly)
EMAIL_TO=recipient@gmail.com
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. (Optional) If pywinauto input fails, run terminal/IDE as Administrator.

## Run

```
# To send an email: ensure EMAIL_TO is set in .env
python talk2mcp.py
```

The agent will instruct Gemini to call:
- `open_paint`
- `draw_rectangle` with coordinates
- `add_text_in_paint` with a text string

## Notes
- UI element coordinates are tuned for standard DPI. If clicks miss, adjust toolbar coordinates inside `functions.py` for `draw_rectangle` and `add_text_in_paint`.
- Ensure no other windows steal focus while automation runs.
- For Gmail: create an App Password under Google Account → Security → 2-Step Verification → App passwords, then use it as `GMAIL_APP_PASSWORD`. Regular account passwords will not work.

