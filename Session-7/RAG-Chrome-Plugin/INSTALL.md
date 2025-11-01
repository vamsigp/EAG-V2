# Installation and Setup Guide

## Quick Setup

1. **Download/Clone the Extension**
   ```bash
   git clone <repository-url>
   cd RAG-Chrome-Plugin
   ```

2. **Create Icon Files** (Required)
   Since icons can't be created programmatically in this environment, you need to create three PNG icon files:
   - `icons/icon16.png` (16x16 pixels)
   - `icons/icon48.png` (48x48 pixels) 
   - `icons/icon128.png` (128x128 pixels)
   
   You can:
   - Use any icon creation tool
   - Download icons from free icon sites
   - Use simple colored squares as placeholders
   - Use the create-icons.js script in a browser environment

3. **Load Extension in Chrome**
   - Open Chrome
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the RAG-Chrome-Plugin folder
   - The extension should now be installed

4. **Verify Installation**
   - Look for the extension icon in the Chrome toolbar
   - Click the icon to open the popup
   - Go to extension options to configure settings

## First Use

1. **Wait for Model Loading**
   - The Universal Sentence Encoder model needs to download (~50MB)
   - This happens automatically when you first visit a page
   - Check the popup to see if the model is loaded

2. **Browse Some Pages**
   - Visit a few web pages with substantial content
   - Avoid confidential sites (they're automatically skipped)
   - Wait a few seconds per page for processing

3. **Test Search**
   - Click the extension icon
   - Enter a search query related to pages you visited
   - You should see similar pages ranked by relevance

## Troubleshooting

### Extension Won't Load
- Make sure all files are present, especially the icon files
- Check that manifest.json is valid JSON
- Look for errors in `chrome://extensions/`

### No Pages Being Indexed
- Check if pages have sufficient content (>200 characters)
- Verify domains aren't in the exclusion list
- Look for console errors in the page's developer tools

### Model Not Loading
- Ensure stable internet connection for initial model download
- Check browser console for TensorFlow.js errors
- Clear extension data and reload if needed

### Performance Issues
- Reduce max index size in options
- Enable automatic cleanup
- Clear old data periodically

## Development Setup

If you want to modify the extension:

1. **Enable Developer Mode**
   - Keep developer mode enabled in `chrome://extensions/`
   - Use "Reload" button when making changes

2. **Debugging**
   - Background script: Inspect service worker from extension details
   - Content script: Use browser developer tools on web pages
   - Popup: Right-click extension icon → "Inspect popup"

3. **Testing**
   - Test on various website types
   - Verify exclusion rules work
   - Test search functionality
   - Check storage limits

## File Structure Checklist

Ensure you have all these files:
- [ ] `manifest.json`
- [ ] `background.js`
- [ ] `content.js`
- [ ] `popup.html`
- [ ] `popup.css`
- [ ] `popup.js`
- [ ] `options.html`
- [ ] `options.css`
- [ ] `options.js`
- [ ] `icons/icon16.png`
- [ ] `icons/icon48.png`
- [ ] `icons/icon128.png`
- [ ] `README.md`

## Security Notes

- The extension only processes content from pages you visit
- All data is stored locally in your browser
- No external servers are contacted except for model loading
- Confidential sites are automatically excluded
- You can add custom domain exclusions in options