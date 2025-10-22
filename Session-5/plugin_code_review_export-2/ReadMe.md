# Gemini Code Review Chrome Extension

This extension allows you to perform AI-powered code reviews on GitHub files using the Gemini API. It provides style review, bug analysis, test suggestions, and a summary for supported code files.

## Recent Changes (September 2025)

### Background Script for API Requests
- **All Gemini API requests are now made from a background script (`background.js`) instead of directly from the content script.**
- This change allows you to inspect all network requests and responses in the Chrome Extension's Service Worker DevTools (chrome://extensions > Inspect Service Worker).
- The content script sends a message to the background script, which performs the actual fetch to the Gemini API and returns the result.
- This is the recommended pattern for Chrome Manifest V3 extensions, as it improves security, debuggability, and transparency.

### How It Works
- When you click "Review with Gemini", the content script sends a message to the background script for each review type (style, bugs, tests, summary).
- The background script makes the POST request to the Gemini API and returns the response to the content script.
- You will see two network requests per review in DevTools: an OPTIONS (pre-flight) and a POST (actual API call). Only the POST counts against your Gemini API quota.

### Inspecting Requests
- Open chrome://extensions, find this extension, and click "Service Worker" under Inspect views.
- Use the Network tab to see all Gemini API requests and responses, including payloads and errors.

### Files Added/Changed
- **background.js**: Handles all Gemini API requests and message passing.
- **manifest.json**: Registers the background script as a service worker.
- **content-script.js**: Now uses `chrome.runtime.sendMessage` to request reviews from the background script.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chrome-gemini-sidebar.git
cd chrome-gemini-sidebar
```

### 2. Configure the Gemini API Key

You need a Gemini API key to use the AI features.

- Go to [Gemini API Console](https://aistudio.google.com/app/apikey) and create an API key.
- Copy the API key.
- Open the extension popup and paste your API key in the provided field.

### 3. Load the Extension in Chrome

1. Go to `chrome://extensions`.
2. Enable "Developer mode" (top right).
3. Click "Load unpacked".
4. Select the extension folder.

### 4. Usage

- Browse to a supported file on GitHub and click "🌟 Review with Gemini".
- Use the sidebar controls to interact with Gemini.
- Inspect network activity in the Service Worker DevTools if needed.

## Code Structure

- `manifest.json` — Extension config.
- `background.js` — Handles Gemini API requests and message passing.
- `content-script.js` — Sidebar logic & Gemini API integration.
- `popup.js` — API key management UI.
- `popup.html` — Popup UI.
- `marked.min.js` — Markdown parser.
- `README.md` — Documentation.

## Security

**Keep your API key private.** Do not share it in public repositories!

## Contributing

Open issues or submit pull requests for improvements.

## License

MIT

---

<div align="center">
  <sub>Made with ❤️ using Gemini and Chat-GPT </sub>
</div>

---