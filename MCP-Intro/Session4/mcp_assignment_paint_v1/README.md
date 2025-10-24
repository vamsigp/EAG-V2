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
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. (Optional) If pywinauto input fails, run terminal/IDE as Administrator.

## Run

```
python talk2mcp.py
```

The agent will instruct Gemini to call:
- `open_paint`
- `draw_rectangle` with coordinates
- `add_text_in_paint` with a text string

## Notes
- UI element coordinates are tuned for standard DPI. If clicks miss, adjust toolbar coordinates inside `functions.py` for `draw_rectangle` and `add_text_in_paint`.
- Ensure no other windows steal focus while automation runs.

