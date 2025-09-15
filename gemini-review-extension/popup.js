document.getElementById("save-key").onclick = function() {
  const key = document.getElementById("api-key").value.trim();
  if (!key) {
    document.getElementById("status").textContent = "Please enter your API key!";
    return;
  }
  chrome.storage.sync.set({ gemini_api_key: key }, function() {
    document.getElementById("status").textContent = "API key saved!";
  });
};

// Autofill if present
chrome.storage.sync.get(["gemini_api_key"], function(result) {
  if (result.gemini_api_key) {
    document.getElementById("api-key").value = result.gemini_api_key;
  }
});