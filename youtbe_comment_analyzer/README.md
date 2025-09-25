# YouTube Comment Analyzer - Chrome Extension

🚀 **Analyze and classify YouTube comments using AI with a beautiful, modern interface**

![Extension Preview](https://img.shields.io/badge/Chrome-Extension-blue?logo=google-chrome)
![AI Powered](https://img.shields.io/badge/AI-Gemini%20Pro-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses Google's Gemini Pro AI to classify comments
- 📊 **Smart Categorization** - Automatically sorts comments into Good, Bad, and Neutral categories  
- 🎨 **Polished UI** - Modern, responsive design with smooth animations
- 🔍 **Smart Filtering** - View comments by category with real-time counts
- 📝 **AI Summary** - Get intelligent summaries of top comments
- 🔒 **Secure** - API keys stored securely in Chrome's encrypted storage
- ⚡ **Fast** - Optimized for performance with up to 50 comments analysis
- 🌙 **Theme Support** - Adapts to YouTube's light/dark theme

## 🛠️ Installation

### Prerequisites
- Google Chrome browser
- Gemini API key ([Get one free here](https://makersuite.google.com/app/apikey))

### Step 1: Download the Extension
1. Download or clone this repository to your computer
2. Make sure all files are in a single folder

### Step 2: Load in Chrome
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **"Developer mode"** (toggle in top right)
3. Click **"Load unpacked"**
4. Select the folder containing the extension files
5. The extension icon should appear in your toolbar

### Step 3: Configure API Key
1. Click the extension icon in your Chrome toolbar
2. Enter your Gemini API key in the configuration section
3. Click **"Save"** - your key is stored securely

## 🎯 Usage

### Analyzing Comments
1. **Navigate to any YouTube video** with comments
2. **Click the extension icon** in your toolbar  
3. **Click "Analyze Comments"** to start AI analysis
4. **View results** categorized as Good 😊, Bad 😞, or Neutral 😐
5. **Filter comments** by clicking category tabs
6. **Get summary** by clicking "Summarize Top 10"

### Features in Detail

#### 🔍 **Comment Classification**
- **Good**: Positive, constructive, helpful, supportive comments
- **Bad**: Negative, toxic, spam, hateful, unconstructive comments  
- **Neutral**: Comments that are neither particularly positive nor negative

#### 📊 **Filtering & Counts**
- View all comments or filter by specific categories
- Real-time counts show distribution across categories
- Smooth transitions between filtered views

#### 📝 **AI Summarization**  
- Intelligent summary of top 10 comments
- Captures main themes and overall sentiment
- Powered by Gemini Pro's advanced language understanding

## 🎨 Screenshots

*Extension popup with polished UI showing comment analysis results*

## ⚙️ Configuration

### API Key Setup
Get your free Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy and paste into the extension

### Advanced Configuration
Edit `config.js` to customize:
- Maximum comments to analyze (default: 50)
- API timeout settings
- UI animation speeds
- Category definitions

## 🔧 Technical Details

### Architecture
- **Manifest V3** - Latest Chrome extension standard
- **Content Script** - Extracts comments from YouTube DOM
- **Background Service Worker** - Handles AI API calls
- **Popup Interface** - Modern UI for interaction and results

### Security
- API keys encrypted in Chrome's secure storage
- No data collection or external tracking
- All processing client-side except AI analysis
- Comments sent only to Google's Gemini API

### Performance
- Optimized for speed with efficient DOM extraction
- Limits analysis to 50 comments for responsiveness
- Caching and smart loading states
- Minimal memory footprint

## 🚨 Troubleshooting

### Common Issues

**"API key not configured"**
- Make sure you've entered a valid Gemini API key
- Check that the key is properly saved

**"No comments found"**  
- Ensure you're on a YouTube video page with visible comments
- Try scrolling down to load more comments first
- Refresh the page if comments aren't loading

**Extension not appearing**
- Make sure all files are in the same folder
- Check that `manifest.json` is present  
- Try disabling and re-enabling the extension

**Analysis taking too long**
- The video might have many comments (limited to first 50)
- Check your internet connection
- API might be rate-limited (wait a few minutes)

### Error Messages
- **API timeout**: Try again in a few minutes
- **Invalid API key**: Double-check your Gemini API key
- **Network error**: Check internet connection

## 📝 File Structure

```
youtube-comment-analyzer/
├── manifest.json          # Extension configuration
├── popup.html            # Main UI interface  
├── popup.css             # Polished styling
├── popup.js              # UI logic and interactions
├── content.js            # YouTube comment extraction
├── content.css           # Content script styles
├── background.js         # AI API integration
├── config.js             # Configuration and setup guide
├── README.md             # This file
└── icons/                # Extension icons (16px, 48px, 128px)
```

## 🔄 Updates

### Version 1.0.0
- Initial release with core functionality
- AI-powered comment classification
- Modern, responsive UI
- Secure API key management
- Comment filtering and summarization

## 📄 License

MIT License - feel free to modify and distribute

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional AI models support
- More classification categories  
- Bulk video analysis
- Export functionality
- Sentiment trending over time

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure you have a valid API key
3. Try refreshing the YouTube page
4. Check Chrome developer console for errors

---

**Made with ❤️ for better YouTube comment analysis**

*This extension helps users understand comment sentiment and find valuable discussions in YouTube videos using the power of AI.*