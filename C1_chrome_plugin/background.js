// Map: tabId => array of redirect URLs
const redirects = {};

// Listen for completed navigation in a tab (record chain)
chrome.webRequest.onBeforeRequest.addListener(
  function (details) {
    // Only track main_frame requests (navigation)
    if (details.type === "main_frame") {
      redirects[details.tabId] = [details.url];
    }
  },
  { urls: ["<all_urls>"] }
);

chrome.webRequest.onBeforeRedirect.addListener(
  function (details) {
    // Append redirected URL
    if (!redirects[details.tabId]) {
      redirects[details.tabId] = [];
    }
    redirects[details.tabId].push(details.redirectUrl);
  },
  { urls: ["<all_urls>"] }
);

// Clean up on tab close
chrome.tabs.onRemoved.addListener(function(tabId, removeInfo) {
  delete redirects[tabId];
});

// Message passing: popup.js asks for redirect chain for the current tab
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "getRedirects") {
    sendResponse({ redirects: redirects[msg.tabId] || [] });
  }
});