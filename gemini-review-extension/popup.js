const apiKeyInput = document.getElementById("api-key");
const status = document.getElementById("status");
const form = document.getElementById("gemini-key-form");
const secureMsg = document.getElementById("secure-message");
const changeKeyBtn = document.getElementById("change-key");
const cancelKeyBtn = document.getElementById("cancel-key");
const lockEmoji = document.getElementById("lock-emoji");

// On load, check for saved key
chrome.storage.sync.get(["gemini_api_key"], function(result) {
  if (result.gemini_api_key) {
    form.style.display = "none";
    secureMsg.style.display = "block";
    status.textContent = "Gemini API key is saved securely.";
    lockEmoji.style.display = "inline";
  } else {
    form.style.display = "block";
    secureMsg.style.display = "none";
    lockEmoji.style.display = "none";
  }
});

// Save key
form.onsubmit = function(e) {
  e.preventDefault();
  const key = apiKeyInput.value.trim();
  if (!key) {
    status.textContent = "Please enter your API key!";
    status.style.color = "red";
    lockEmoji.style.display = "none";
    return;
  }
  chrome.storage.sync.set({ gemini_api_key: key }, function() {
    apiKeyInput.value = "";
    form.style.display = "none";
    secureMsg.style.display = "block";
    status.textContent = "Gemini API key is saved securely.";
    status.style.color = "#225bb0";
    lockEmoji.style.display = "inline";
  });
};

// Show change key form
changeKeyBtn.onclick = function() {
  form.style.display = "block";
  secureMsg.style.display = "none";
  lockEmoji.style.display = "none";
  apiKeyInput.value = "";
  status.textContent = "";
  apiKeyInput.focus();
};

// Cancel change, revert to secure state
cancelKeyBtn.onclick = function() {
  form.style.display = "none";
  secureMsg.style.display = "block";
  status.textContent = "Gemini API key is saved securely.";
  status.style.color = "#225bb0";
  lockEmoji.style.display = "inline";
  apiKeyInput.value = "";
};