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
  // GitHub file view: textarea!
  const ta = document.querySelector('textarea[data-testid="read-only-cursor-text-area"]');
  if (ta && ta.value) return ta.value;
  return null;
}

function insertSidebar() {
  if (document.getElementById("gemini-review-sidebar")) return;
  const sidebar = document.createElement("div");
  sidebar.id = "gemini-review-sidebar";
  sidebar.innerHTML = `
    <div class="gemini-review-header">
      <span class="gemini-title">Gemini AI Code Review</span>
      <button id="gemini-review-close" title="Close">&times;</button>
    </div>
    <button id="gemini-review-submit" class="gemini-review-btn">Review this code</button>
    <div id="gemini-review-loading" class="gemini-review-loading" style="display:none;">Analyzing…</div>
    <div id="gemini-review-content" class="gemini-review-content"></div>
  `;
  sidebar.style = `
    position:fixed; top:60px; right:18px; width:430px; z-index:99999;
    height:82vh; background:#fff; color:#222; border:1px solid #e2e2e4;
    border-radius:8px; box-shadow:-2px 2px 16px -2px #0002; padding:0; 
    font-family: 'Segoe UI', 'Roboto', Arial,sans-serif;
    display: flex; flex-direction: column;
  `;
  document.body.appendChild(sidebar);

  // Internal CSS for markdown
  const styleTag = document.createElement("style");
  styleTag.textContent = `
    #gemini-review-sidebar .gemini-review-header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 11px 16px 10px 16px; border-bottom: 1px solid #eee; background: #f7f7fa;
      border-radius:8px 8px 0 0;
    }
    #gemini-review-sidebar .gemini-title { font-weight: bold; font-size: 1.1rem; color: #3276e3; }
    #gemini-review-close { background: #f2f2f2; border:none; color:#444; font-size:1.3em; cursor:pointer; padding: 0 0.39em; border-radius:5px; }
    #gemini-review-close:hover { background:#e0e3eb; }
    #gemini-review-submit { margin: 16px auto 10px auto; display:block; background: #3276e3; color:#fff; border:none; font-size:1em; border-radius:5px; padding:8px 22px; cursor:pointer; box-shadow: 0 2px 8px -2px #3276e333; }
    #gemini-review-submit:hover { background: #225bb0;}
    #gemini-review-loading { margin:9px auto 0 auto; color: #225bb0; font-style:italic;}
    #gemini-review-content { margin:10px 15px 15px 15px; overflow-y: auto; flex-grow: 1; background:#fafbfc; border-radius:10px; padding:18px; border:1px solid #eee; min-height:120px; max-height:60vh; box-shadow: 0 2px 8px 0 #f0f0f4;}
    #gemini-review-content h1, #gemini-review-content h2, #gemini-review-content h3 { color:#3276e3; font-weight:700 !important; margin-top:18px; margin-bottom:8px; font-family:inherit;}
    #gemini-review-content p { margin: 10px 0; font-size: 1.04em;}
    #gemini-review-content ul { margin-top:8px; margin-left:1.2em;}
    #gemini-review-content li { margin-bottom:7px; font-size:1.03em;}
    #gemini-review-content strong { color: #225bb0; font-weight: bold;}
    #gemini-review-content code, #gemini-review-content pre {
      background: #f4f2fa;
      border-radius: 5px;
      padding: 7px;
      font-size: 0.98em;
      font-family: 'Fira Mono', 'Consolas', 'Monaco', monospace;
      color: #222;
    }
    #gemini-review-content pre { overflow-x: auto; margin-top:12px;}
    #gemini-review-content blockquote {
      border-left: 3px solid #c7dfe6;
      padding-left:12px; margin:10px 0; color:#666; background: #f6f7fa; border-radius:4px;
    }
    #gemini-review-content table { border-collapse: collapse; margin-top:14px;}
    #gemini-review-content th, #gemini-review-content td { border:1px solid #ddd; padding:5px 11px; font-size: 0.98em; }
  `;
  document.head.appendChild(styleTag);

  document.getElementById("gemini-review-close").onclick = function() {
    sidebar.remove();
    styleTag.remove();
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
    reviewContent.innerHTML = "";

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
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + apiKey,
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
        reviewContent.innerHTML = marked.parse(reply);
      } catch (e) {
        reviewContent.textContent = "Error: " + e;
        console.error(e);
      }
      document.getElementById("gemini-review-loading").style.display = "none";
    });
  };
}

if (getFileExtension()) {
  insertSidebar();
}