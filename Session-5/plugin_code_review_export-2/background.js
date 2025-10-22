// background.js
// Handles Gemini API requests so they are visible in extension background DevTools

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  if (message.type === "GEMINI_API_REQUEST") {
    const { prompt, apiKey, model } = message;
    console.log("[Gemini BG] Request received", { prompt, apiKey: apiKey ? "***" : undefined, model });
    (async () => {
      try {
        const response = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
          }
        );
        const data = await response.json();
        console.log("[Gemini BG] Response", data);
        sendResponse({ success: true, data });
      } catch (e) {
        console.error("[Gemini BG] Error", e);
        sendResponse({ success: false, error: e.toString() });
      }
    })();
    // Return true synchronously to keep the message channel open
    return true;
  }
});
