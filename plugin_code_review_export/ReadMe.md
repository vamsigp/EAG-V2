# Chrome Sidebar Extension

A Chrome extension that adds a sidebar to any webpage, allowing you to interact with Gemini via Google's AI API.

## Features

- **Sidebar UI:** Easily accessible sidebar on any website.
- **Toggle Sidebar:** Open and close the sidebar using provided controls.
- **Connect to Gemini API:** Interact with Google’s Gemini AI via the API.
- **Simple Setup:** Quick installation and configuration.

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

#### Where to Add Your API Key

Edit `content-script.js` (or your configuration file) and replace `"YOUR_GEMINI_API_KEY"` with your actual key:

```js
const GEMINI_API_KEY = "YOUR_GEMINI_API_KEY";
```

### 3. Load the Extension in Chrome

1. Go to `chrome://extensions`.
2. Enable "Developer mode" (top right).
3. Click "Load unpacked".
4. Select the `chrome-gemini-sidebar` folder.

### 4. Usage

- Click the extension icon to open the sidebar.
- Use the sidebar controls to interact with Gemini.
- Click the close button to hide the sidebar.

## Code Structure

- `manifest.json` — Extension config.
- `content-script.js` — Sidebar logic & Gemini API integration.
- `sidebar.html` & `sidebar.css` — Sidebar UI/templates.
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