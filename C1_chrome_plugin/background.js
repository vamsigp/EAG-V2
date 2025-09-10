// Map: tabId => array of redirect URLs
const redirects = {};
// Map: tabId => bandwidth in bytes
const bandwidth = {};

// Listen for navigation to start (reset bandwidth and redirects)
chrome.webRequest.onBeforeRequest.addListener(
  function (details) {
    if (details.type === "main_frame") {
      redirects[details.tabId] = [details.url];
      bandwidth[details.tabId] = 0;
    }
  },
  { urls: ["<all_urls>"] }
);

// Track redirect chain
chrome.webRequest.onBeforeRedirect.addListener(
  function (details) {
    if (!redirects[details.tabId]) {
      redirects[details.tabId] = [];
    }
    redirects[details.tabId].push(details.redirectUrl);
  },
  { urls: ["<all_urls>"] }
);

// Sum all resource loads on this tab (try all requests for tab)
chrome.webRequest.onCompleted.addListener(
  function(details) {
    if (typeof bandwidth[details.tabId] === "undefined") return;
    // Try to get content-length header
    let contentLength = 0;
    if (details.responseHeaders) {
      for (let h of details.responseHeaders) {
        if (h.name.toLowerCase() === 'content-length') {
          contentLength = parseInt(h.value) || 0;
        }
      }
    }
    bandwidth[details.tabId] += contentLength;
  },
  {
    urls: ["<all_urls>"],
    types: ["main_frame", "sub_frame", "script", "xmlhttprequest", "stylesheet", "image", "font", "other"]
  },
  ["responseHeaders"]
);

// Clean up on tab close
chrome.tabs.onRemoved.addListener(function(tabId, removeInfo) {
  delete redirects[tabId];
  delete bandwidth[tabId];
});

// Message passing for popup.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "getTabData") {
    sendResponse({
      redirects: redirects[msg.tabId] || [],
      bandwidth: bandwidth[msg.tabId] || 0
    });
  }
});