// Content script for extracting YouTube comments
let commentsData = [];
let isAnalyzing = false;

// Wait for page to load and inject our functionality
function init() {
  if (window.location.hostname !== 'www.youtube.com') return;
  
  // Wait a bit for YouTube's dynamic content to load
  setTimeout(() => {
    extractComments();
    injectAnalyzeButton();
  }, 2000);
}

async function extractComments() {
  console.log('🔍 Starting comment extraction...');
  
  // Try multiple selectors for better comment detection
  const selectors = [
    'ytd-comment-thread-renderer #content-text',
    'ytd-comment-renderer #content-text',
    '.ytd-comment-thread-renderer #content-text',
    '#content-text'
  ];
  
  let commentElements = [];
  for (const selector of selectors) {
    commentElements = document.querySelectorAll(selector);
    if (commentElements.length > 0) {
      console.log(`✅ Found ${commentElements.length} comments using selector: ${selector}`);
      break;
    }
  }
  
  // If still no comments, try to scroll and load more
  if (commentElements.length < 30) {
    console.log('📜 Attempting to load more comments by scrolling...');
    await scrollToLoadMoreComments();
    
    // Try again after scrolling
    for (const selector of selectors) {
      commentElements = document.querySelectorAll(selector);
      if (commentElements.length > 0) {
        console.log(`✅ After scrolling, found ${commentElements.length} comments`);
        break;
      }
    }
  }
  
  commentsData = Array.from(commentElements)
    .map(element => element.textContent.trim())
    .filter(text => text.length > 0 && text.length < 1000) // Filter out very long comments (likely not real comments)
    .slice(0, 100); // Increased limit to 100 comments
  
  console.log(`📊 Final extraction result: ${commentsData.length} comments`);
  console.log('📝 Sample comments:', commentsData.slice(0, 3));
}

function injectAnalyzeButton() {
  // Remove existing button if present
  const existingButton = document.getElementById('yt-comment-analyzer-btn');
  if (existingButton) {
    existingButton.remove();
  }

  // Find a good place to inject our button (next to like/dislike buttons)
  const actionsBar = document.querySelector('#top-level-buttons-computed');
  if (!actionsBar) return;

  const analyzeButton = document.createElement('button');
  analyzeButton.id = 'yt-comment-analyzer-btn';
  analyzeButton.className = 'yt-comment-analyzer-button';
  analyzeButton.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
    </svg>
    Analyze Comments
  `;
  
  analyzeButton.addEventListener('click', async () => {
    analyzeButton.textContent = 'Loading Comments...';
    analyzeButton.disabled = true;
    
    await extractComments();
    
    if (commentsData.length === 0) {
      alert('No comments found. Please make sure you are on a YouTube video page with comments.');
      analyzeButton.textContent = 'Analyze Comments';
      analyzeButton.disabled = false;
      return;
    }
    
    // Store comments for popup to access
    chrome.storage.local.set({ 
      comments: commentsData,
      videoUrl: window.location.href,
      timestamp: Date.now()
    });
    
    analyzeButton.textContent = 'Analyze Comments';
    analyzeButton.disabled = false;
    
    // Open popup - not needed as user will click extension icon
    console.log(`✅ ${commentsData.length} comments ready for analysis`);
  });

  actionsBar.appendChild(analyzeButton);
}

// Re-inject when navigating to new videos (YouTube is SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    setTimeout(init, 1000);
  }
}).observe(document, { subtree: true, childList: true });

// Initialize when content script loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getComments') {
    extractComments().then(() => {
      sendResponse({ comments: commentsData });
    });
    return true; // Keep message channel open for async response
  }
});

// Scroll to load more comments function
async function scrollToLoadMoreComments() {
  return new Promise((resolve) => {
    console.log('📜 Scrolling to load more comments...');
    
    const commentsSection = document.querySelector('#comments');
    if (!commentsSection) {
      console.log('❌ Comments section not found');
      resolve();
      return;
    }
    
    // Scroll to comments section first
    commentsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Wait a bit, then scroll down multiple times to load more comments
    setTimeout(() => {
      let scrollAttempts = 0;
      const maxScrolls = 3;
      
      const scrollInterval = setInterval(() => {
        window.scrollBy(0, 500);
        scrollAttempts++;
        
        if (scrollAttempts >= maxScrolls) {
          clearInterval(scrollInterval);
          console.log('✅ Completed scrolling attempts');
          // Wait a bit more for comments to load
          setTimeout(resolve, 1500);
        }
      }, 800);
    }, 1000);
  });
}

// Legacy function - keeping for compatibility
function loadMoreComments() {
  return scrollToLoadMoreComments();
}