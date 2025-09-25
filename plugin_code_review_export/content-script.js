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
  const ta = document.querySelector('textarea[data-testid="read-only-cursor-text-area"]');
  if (ta && ta.value) return ta.value;
  return null;
}

function insertSidebar() {
  if (document.getElementById("gemini-review-sidebar")) return;
  
  // Create Sidebar
  const sidebar = document.createElement("div");
  sidebar.id = "gemini-review-sidebar";
  // Left drag handle (visible)
  sidebar.innerHTML = `
    <div id="left-resize-handle" style="
      width:12px; height:100%; position:absolute; left:0; top:0; z-index:10010; cursor:ew-resize;
      background:transparent; display:flex; align-items:center; justify-content:center;">
      <div style="width:6px;height:44px; background:#e7ecf1; border-radius:9px; margin-left:2px; margin-top:4px;opacity:0.7;"></div>
    </div>
    <div class="gemini-review-header">
      <span class="gemini-title">Gemini AI Code Review</span>
      <button id="gemini-review-close" title="Close">&times;</button>
    </div>
    <button id="gemini-review-submit" class="gemini-review-btn">Review this code</button>
    <div id="gemini-review-progress"></div>
    <div id="gemini-review-content" class="gemini-review-content"></div>
  `;
  sidebar.style = `
    position:fixed; top:60px; right:18px; min-width:350px; max-width:80vw; width:430px;
    z-index:99999; height:82vh; background:#fff; color:#222; border:1px solid #e2e2e4;
    border-radius:11px; box-shadow:-2px 2px 22px -2px #0002; padding:0;
    font-family: 'Segoe UI', 'Roboto', Arial,sans-serif;
    display: flex; flex-direction: column;
    overflow: visible; transition: width 0.1s;`;

  document.body.appendChild(sidebar);

  // Setup left drag handle for resizing
  const leftHandle = sidebar.querySelector('#left-resize-handle');
  let isDragging = false, startX = 0, startW = 0;
  leftHandle.addEventListener('mousedown', function(e) {
    isDragging = true;
    startX = e.clientX;
    startW = sidebar.offsetWidth;
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });
  window.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    const delta = startX - e.clientX;
    let newWidth = Math.max(320, Math.min(window.innerWidth - 36, startW + delta));
    sidebar.style.width = newWidth + "px";
  });
  window.addEventListener('mouseup', function() {
    if (isDragging) {
      document.body.style.userSelect = '';
      isDragging = false;
    }
  });

  // Internal CSS
  const styleTag = document.createElement("style");
  styleTag.textContent = `
    #gemini-review-sidebar .gemini-review-header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 11px 16px 10px 16px; border-bottom: 1px solid #eee; background: #f7f7fa;
      border-radius:11px 11px 0 0;
    }
    #gemini-review-sidebar .gemini-title { font-weight: bold; font-size: 1.1rem; color: #3276e3; }
    #gemini-review-close { background: #f2f2f2; border:none; color:#444; font-size:1.3em; cursor:pointer; padding: 0 0.39em; border-radius:8px; }
    #gemini-review-close:hover { background:#e0e3eb; }
    #gemini-review-submit { margin: 16px auto 10px auto; display:block; background: #3276e3; color:#fff; border:none; font-size:1em; border-radius:7px; padding:8px 22px; cursor:pointer; box-shadow: 0 2px 8px -2px #3276e333; }
    #gemini-review-submit:hover { background: #225bb0;}
    /* Progress steps */
    #gemini-review-progress { margin: 12px 17px 0 17px; display: flex; flex-direction: column; gap: 7px;}
    .step-row {
      display: flex; align-items: center; gap:9px; font-size:1.05em; margin-bottom:0px; padding: 3px 0;
    }
    .step-spinner {
      width:18px; height:18px; display:inline-block; border:3px solid #b8dcf8; border-top:3px solid #25aecd; border-radius:50%; animation:spin 0.9s linear infinite;
      margin-right:3px; vertical-align: middle;
    }
    @keyframes spin { 100% { transform:rotate(360deg); } }
    .step-done { color:#1bcb25; font-weight:bold; font-size:1.25em; margin-right: -3px;}
    .step-timer { font-size: 0.97em; color:#888; margin-left:6px;}
    /* Results */
    #gemini-review-content { margin:12px 15px 15px 15px; overflow-y: auto; flex-grow: 1; background:#fafbfc; border-radius:10px; padding:18px; border:1px solid #eee; min-height:110px; max-height:60vh; box-shadow: 0 2px 8px 0 #f0f0f4;}
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
    #left-resize-handle { background:transparent; }
    #left-resize-handle:hover > div { background:#d1eafe; opacity:0.9;}
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
    const progressDiv = document.getElementById("gemini-review-progress");
    if (!ext || !code) {
      reviewContent.textContent = "Cannot detect file type or code.";
      return;
    }
    reviewContent.innerHTML = "";
    progressDiv.innerHTML = "";
    chrome.storage.sync.get(['gemini_api_key'], async function(result) {
      const apiKey = result.gemini_api_key;
      if (!apiKey) {
        reviewContent.textContent = "Gemini API key not set.";
        return;
      }
      await runGeminiChain(ext, code, apiKey, reviewContent, progressDiv);
    });
  };
}

// Review chain
const geminiTasks = [
  {
    name: "Style Review",
    prompt: (ext, code) => `Review this ${ext} code ONLY for style/readability. Formatting, conventions, naming, idioms, best practices. Markdown, sections for strengths & weaknesses.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``
  },
  {
    name: "Bug Analysis",
    prompt: (ext, code) => `Analyze for bugs, logic errors, edge cases or failure points in this ${ext} code. List problems and fixes. Markdown.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``
  },
  {
    name: "Test Suggestions",
    prompt: (ext, code) => `Suggest unit and integration test cases for this ${ext} code. Provide code snippets if possible. Markdown.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``
  },
  {
    name: "Summary",
    prompt: (ext, code) => `Summarize what this ${ext} code does. Concise, markdown.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``
  }
];

async function runGeminiChain(ext, code, apiKey, reviewContent, progressDiv) {
  progressDiv.innerHTML = geminiTasks.map((task, i) =>
    `<div class="step-row" id="step-row-${i}">
      <span class="step-spinner" id="spinner-${i}"></span>
      <span id="step-label-${i}">${task.name}</span>
      <span class="step-timer" id="step-timer-${i}"></span>
    </div>`
  ).join('');
  for (let i = 0; i < geminiTasks.length; ++i) {
    const task = geminiTasks[i];
    // Previous steps -- set checkmark and elapsed seconds
    if (i > 0) {
      document.getElementById(`spinner-${i-1}`).style.display = "none";
      document.getElementById(`step-row-${i-1}`).insertAdjacentHTML("afterbegin", `<span class="step-done">✅</span>`);
      // Timer stays, set font color to green on step-timer
      document.getElementById(`step-timer-${i-1}`).style.color = "#139c13";
    }
    document.getElementById(`step-label-${i}`).style.fontWeight = "bold";

    // Time the API call
    const t0 = performance.now();
    const reply = await callGeminiAPI(task.prompt(ext, code), apiKey);
    const t1 = performance.now();
    const seconds = ((t1 - t0)/1000).toFixed(2);

    document.getElementById(`step-timer-${i}`).textContent = `(${seconds}s)`;

    reviewContent.innerHTML += `<div style="margin-top:10px;margin-bottom:28px;padding:11px 13px;background:#f9fbff;border-radius:7px;box-shadow:0 0 4px #e0eaff;">
      <h2 style="margin-bottom:11px;color:#267bdb">${task.name}</h2>
      ${marked.parse(reply)}
      </div>`;
  }
  let last = geminiTasks.length-1;
  document.getElementById(`spinner-${last}`).style.display = "none";
  document.getElementById(`step-row-${last}`).insertAdjacentHTML("afterbegin", `<span class="step-done">✅</span>`);
  document.getElementById(`step-label-${last}`).style.fontWeight = "bold";
  document.getElementById(`step-timer-${last}`).style.color = "#139c13";
  progressDiv.innerHTML += `<div style="margin-top:12px;color:green;font-size:1.08em;"><b>All reviews completed!</b></div>`;
}

async function callGeminiAPI(prompt, apiKey) {
  try {
    // Use gemini-2.0-flash (if publicly available, else revert to gemini-1.5-flash)
    const response = await fetch(
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + apiKey,
      {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({contents: [{parts: [{text: prompt}]}]})
      }
    );
    const data = await response.json();
    if (data && data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts[0]) {
      return data.candidates[0].content.parts[0].text;
    }
    return "No response from Gemini.";
  } catch(e) {
    return "Error: " + e;
  }
}

if (getFileExtension()) {
  insertSidebar();
}