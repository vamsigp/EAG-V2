const EXTENSIONS = [".kt", ".java", ".cpp", ".c", ".py", ".gradle.kts", ".gradle"];

function getFileExtension() {
  const parts = window.location.pathname.split("/");
  if (parts.length < 6) return null;
  const filename = parts.slice(5).join("/");
  for (let ext of EXTENSIONS) {
    if (filename.endsWith(ext)) return ext;
  }
  return null;
}

function extractSourceCode() {
  // GitHub's new file view: textarea!
  const ta = document.querySelector('textarea[data-testid="read-only-cursor-text-area"]');
  if (ta && ta.value) return ta.value;
  return null;
}

function insertSidebar() {
  if (document.getElementById("gemini-review-sidebar")) return;
  const sidebar = document.createElement("div");
  sidebar.id = "gemini-review-sidebar";
  sidebar.innerHTML = `
    <button id="gemini-review-close">×</button>
    <div style="font-weight:bold;">Gemini Code Review</div>
    <button id="gemini-review-submit">Review this code</button>
    <div id="gemini-review-content"></div>
    <div id="gemini-review-loading" style="display:none;">Analyzing…</div>
  `;
  sidebar.style = "position:fixed;top:60px;right:0;width:400px;z-index:99999;height:80vh;background:#fff;color:#222;border-left:1px solid #dedede;box-shadow:-2px 0 8px -2px #0002;padding:16px;overflow:auto;font-family:sans-serif;";
  document.body.appendChild(sidebar);

  document.getElementById("gemini-review-close").onclick = function() {
    sidebar.remove();
  };
  document.getElementById("gemini-review-submit").onclick = function() {
    const ext = getFileExtension();
    const code = extractSourceCode();
    const reviewContent = document.getElementById("gemini-review-content");
    if (!ext || !code) {
      reviewContent.textContent = "Cannot detect file type or code.";
      return;
    }
    document.getElementById("gemini-review-loading").style.display = "block";
    reviewContent.textContent = "";
    chrome.storage.sync.get(['gemini_api_key'], async function(result) {
      const apiKey = result.gemini_api_key;
      if (!apiKey) {
        reviewContent.textContent = "Gemini API key not set.";
        document.getElementById("gemini-review-loading").style.display = "none";
        return;
      }
      try {
        const prompt = `You are a senior software engineer. Please review the following ${ext} source code for bugs, best practices, code style and improvement opportunities. Reply in markdown with clear sections for summary, possible issues, suggestions, and praise.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``;
        const response = await fetch(
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + apiKey,
          {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({contents: [{parts: [{text: prompt}]}]})
          }
        );
        const data = await response.json();
        let reply = "Could not get review. Network/error.";
        if (data && data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts[0]) {
          reply = data.candidates[0].content.parts[0].text;
        }
        reviewContent.innerHTML = reply;
      } catch (e) {
        reviewContent.textContent = "Error: " + e;
      }
      document.getElementById("gemini-review-loading").style.display = "none";
    });
  };
}

if (getFileExtension()) {
  insertSidebar();
}