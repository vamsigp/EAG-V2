// Configuration file for YouTube Comment Analyzer
// You can modify the API key and other settings here

const CONFIG = {
  // Add your Gemini API key here (or configure through the extension popup)
  // Get your API key from: https://makersuite.google.com/app/apikey
  GEMINI_API_KEY: '', // Leave empty to configure through UI
  
  // API Configuration
  API_BASE_URL: 'https://generativelanguage.googleapis.com/v1beta',
  MODEL_NAME: 'gemini-2.0-flash',
  
  // Extension Settings
  MAX_COMMENTS_TO_ANALYZE: 100, // Maximum number of comments to analyze at once
  ANALYSIS_TIMEOUT: 30000, // 30 seconds timeout for API calls
  
  // Comment Categories
  CATEGORIES: {
    GOOD: 'Good',
    NEUTRAL: 'Neutral', 
    BAD: 'Bad'
  },
  
  // UI Settings
  ANIMATION_DURATION: 200, // milliseconds
  NOTIFICATION_DURATION: 5000, // 5 seconds
  
  // YouTube Selectors (may need updates if YouTube changes their DOM)
  SELECTORS: {
    COMMENTS: 'ytd-comment-thread-renderer #content-text',
    ACTIONS_BAR: '#top-level-buttons-computed',
    COMMENTS_SECTION: '#comments'
  }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}

// Make available globally for browser environment
if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
}

/*
SETUP INSTRUCTIONS:
===================

1. Get your Gemini API key:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Create a new API key
   - Copy the key

2. Configure the API key:
   Option A: Use the extension popup UI (recommended)
   - Click on the extension icon
   - Enter your API key in the configuration section
   
   Option B: Edit this file directly
   - Replace the empty GEMINI_API_KEY value above with your key
   - Example: GEMINI_API_KEY: 'AIzaSyC1234567890abcdef...'

3. Load the extension:
   - Open Chrome and go to chrome://extensions/
   - Enable "Developer mode" (top right toggle)
   - Click "Load unpacked"
   - Select the folder containing these files
   
4. Test the extension:
   - Go to any YouTube video with comments
   - Click the extension icon
   - Click "Analyze Comments" to start

TROUBLESHOOTING:
================

- "API key not configured" error:
  Make sure you've entered a valid API key either through the UI or in this file

- "No comments found" error:
  Make sure you're on a YouTube video page with visible comments

- API timeout errors:
  The video might have too many comments. The extension limits analysis to the first 50 comments for performance.

- Extension not appearing:
  Make sure all files are in the same folder and the manifest.json is present

FEATURES:
=========

✅ Extract comments from YouTube videos
✅ Classify comments as Good, Bad, or Neutral using AI
✅ Filter comments by category
✅ Summarize top 10 comments
✅ Polished, responsive UI
✅ Secure API key storage
✅ Error handling and notifications
✅ Dark/light theme support
✅ Loading states and animations

LIMITATIONS:
============

- Requires active internet connection for AI analysis
- Gemini API has rate limits (generous free tier available)  
- Only analyzes first 50 comments for performance
- Requires YouTube to be loaded completely before analysis
- Extension needs to be manually loaded in developer mode

PRIVACY:
========

- Comments are sent to Google's Gemini API for analysis
- API key is stored locally in Chrome's secure storage
- No data is collected or stored by this extension
- All processing happens client-side except AI analysis
*/