# RAG Web Indexer Chrome Extension

A Chrome extension that automatically builds embeddings for web pages you visit and creates a searchable FAISS-like index for semantic search.

## Features

- **Automatic Page Processing**: Extracts content from web pages as you browse
- **Smart Filtering**: Skips confidential sites like Gmail, WhatsApp, banking sites, etc.
- **Semantic Embeddings**: Uses TensorFlow.js Universal Sentence Encoder for high-quality embeddings
- **FAISS-like Search**: Implements cosine similarity search for finding similar pages
- **Persistent Storage**: Stores embeddings and metadata locally using Chrome storage API
- **Search Interface**: Clean popup interface for searching indexed content
- **Configuration**: Customizable settings for excluded domains and processing parameters

## Installation

1. Clone or download this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the extension directory
5. The extension icon should appear in your toolbar

## Usage

### Automatic Indexing
- Simply browse the web normally
- The extension automatically processes pages after a 2-second delay
- Pages with insufficient content (<200 characters) are skipped
- Confidential domains are automatically excluded

### Searching
1. Click the extension icon in the toolbar
2. Enter your search query in the popup
3. View results ranked by similarity
4. Click any result to open that page

### Configuration
1. Right-click the extension icon and select "Options"
2. Add custom domains to exclude
3. Adjust processing settings
4. Manage your indexed data

## Technical Details

### Architecture
- **Content Script**: Extracts page content and filters confidential sites
- **Background Service Worker**: Handles embedding generation and index management
- **Popup Interface**: Provides search functionality and recent pages view
- **Options Page**: Configuration and data management

### Embedding Model
- Uses TensorFlow.js Universal Sentence Encoder
- Generates 512-dimensional embeddings
- Runs entirely in the browser (no external API calls)

### Storage
- Index data stored in Chrome local storage
- Settings stored in Chrome sync storage
- Automatic cleanup when storage limits are reached

### Excluded Domains (Default)
- mail.google.com
- gmail.com
- web.whatsapp.com
- accounts.google.com
- login.microsoftonline.com
- github.com/login
- paypal.com
- stripe.com
- Any page with 'login', 'signin', or 'auth' in the URL

## Performance

- Model loads automatically on extension startup
- Embeddings generated asynchronously to avoid blocking
- Content limited to 10,000 characters per page
- Implements similarity search with cosine distance
- Memory efficient with automatic cleanup

## Privacy

- All processing happens locally in your browser
- No data is sent to external servers
- You control what gets indexed through domain exclusions
- Data can be exported/imported for backup purposes

## Configuration Options

### Processing Settings
- **Minimum Content Length**: Pages smaller than this are ignored (default: 200 chars)
- **Maximum Content Length**: Content is truncated to this length (default: 10,000 chars)
- **Processing Delay**: Wait time before processing pages (default: 2 seconds)
- **SPA Detection**: Automatically detect content changes in single-page applications

### Storage Settings
- **Maximum Index Size**: Limit on number of indexed pages (default: 1,000)
- **Automatic Cleanup**: Remove oldest entries when limit is reached

### Domain Management
- Add custom domains to exclude from indexing
- View and manage the default exclusion list

## Development

### File Structure
```
├── manifest.json          # Extension manifest
├── background.js          # Service worker for embeddings and indexing
├── content.js             # Content script for page processing
├── popup.html/css/js      # Extension popup interface
├── options.html/css/js    # Options page for configuration
├── icons/                 # Extension icons
└── README.md             # This file
```

### Dependencies
- TensorFlow.js (loaded from CDN)
- Universal Sentence Encoder model (loaded from CDN)

### Building
No build process required. The extension runs directly from source files.

## Troubleshooting

### Model Not Loading
- Check internet connection (model loads from CDN)
- Wait a few seconds after installation for model to download
- Check browser console for error messages

### Pages Not Being Indexed
- Verify the page has sufficient content (>200 characters)
- Check if the domain is in the exclusion list
- Look for console messages in the page's developer tools

### Search Not Working
- Ensure the embedding model has loaded successfully
- Check that you have indexed pages to search through
- Try different search terms or queries

### Storage Issues
- Check available storage in chrome://settings/content/all
- Use the "Clear All Data" option to reset if needed
- Consider reducing the maximum index size setting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with different websites
5. Submit a pull request

## License

This project is open source. Please respect the privacy and security considerations when using or modifying the code.

## Changelog

### Version 1.0.0
- Initial release
- Automatic page content extraction
- Universal Sentence Encoder integration
- FAISS-like similarity search
- Chrome storage integration
- Popup search interface
- Options page for configuration
- Domain exclusion system
- Export/import functionality