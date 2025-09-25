const GEMINI_API_MODEL = "gemini-2.0-flash";
const SUPPORTED_EXTENSIONS = [".kt", ".java", ".cpp", ".c", ".py", ".gradle.kts", ".gradle"];
const GEMINI_TABS = [
  { key: "style",    name: "Style Review" },
  { key: "bugs",     name: "Bug Analysis" },
  { key: "tests",    name: "Test Suggestions" },
  { key: "summary",  name: "Summary" }
];
const THEME = {
  colorMain: "#0a9556",
  colorMainHover: "#067946",
  colorAccent: "#3276e3"
};

// UTILS
function getGitHubFileExtension() {
  const parts = window.location.pathname.split("/");
  if (parts.length < 6) return null;
  const filename = parts.slice(5).join("/");
  return SUPPORTED_EXTENSIONS.find(ext => filename.endsWith(ext)) || null;
}
function getGitHubSourceCode() {
  const ta = document.querySelector('textarea[data-testid="read-only-cursor-text-area"]');
  return ta && ta.value ? ta.value : null;
}
function isSupportedFilePage() { return getGitHubFileExtension() !== null; }

// OOP Main Review UI
class GeminiReviewUI {
  constructor() {
    this.state = { sidebar: null, tabResults: {}, tabRawMarkdown: {} };
    if (isSupportedFilePage()) this.injectFloatingButton();
  }
  injectFloatingButton() {
    if (document.getElementById("gemini-review-float-btn")) return;
    const btn = document.createElement("button");
    btn.id = "gemini-review-float-btn";
    btn.textContent = "🌟 Review with Gemini";
    btn.style = `
      position: fixed; bottom: 34px; right: 34px; z-index:10050; padding:15px 18px;
      background: ${THEME.colorMain}; color: #fff; font-weight:600; border:none;
      border-radius:14px; font-size:1.15em; box-shadow: 0 8px 22px -5px #8883; cursor:pointer;
      transition: background 0.2s; outline:none;
    `;
    btn.onmouseenter = () => { btn.style.background = THEME.colorMainHover; };
    btn.onmouseleave = () => { btn.style.background = THEME.colorMain; };
    btn.addEventListener("click", () => this.openSidebar());
    document.body.appendChild(btn);
  }
  openSidebar() {
    if (this.state.sidebar) {
      this.state.sidebar.style.display = "block";
      return;
    }
    this.renderSidebar();
  }
  renderSidebar() {
    let old = document.getElementById("gemini-review-sidebar");
    if (old) old.remove();

    // --- Layout --
    const sidebar = document.createElement("div");
    sidebar.id = "gemini-review-sidebar";
    sidebar.innerHTML = `
      <div id="left-resize-handle"></div>
      <div class="gemini-review-header">
        <span class="gemini-title">Gemini AI Code Review</span>
        <button id="gemini-review-close" title="Close">&times;</button>
      </div>
      <button id="gemini-review-submit" class="gemini-review-btn"
        style="background:${THEME.colorMain};color:#fff;font-weight:700;border:none;border-radius:7px;font-size:1.1em;padding:11px 27px;margin:22px auto 0 auto;display:block;cursor:pointer;box-shadow:0 2px 8px -2px #35b68147;">
        Review this code
      </button>
      <div id="gemini-tabs-bar-wrap" style="overflow-x:auto;overflow-y:hidden;margin: 14px 0 0 0;scrollbar-width:thin;background:#fff;border-radius:9px 9px 0 0;min-height:40px;">
        <div id="gemini-tabs-bar" style="display:flex;min-width:340px;white-space:nowrap;"></div>
      </div>
      <div id="gemini-tab-content" class="gemini-review-content"></div>
      <div style="margin-top:0;display:flex;flex-direction:column;">
        <div id="gemini-review-progress"></div>
        <div id="gemini-export-area" style="height:44px;display:flex;align-items:center;justify-content:flex-end;padding:10px 30px 0 0;"></div>
      </div>
    `;
    sidebar.style = `
      position:fixed; top:60px; right:18px; min-width:350px; max-width:80vw; width:520px;
      z-index:99999; height:92vh; background:#fff; color:#222; border:1px solid #e2e2e4;
      border-radius:13px; box-shadow:-2px 2px 22px -2px #0002; padding:0;
      font-family: 'Segoe UI', 'Roboto', Arial,sans-serif; display:flex; flex-direction:column; overflow:visible; transition: width 0.1s;
    `;
    document.body.appendChild(sidebar);

    this.state.sidebar = sidebar;
    this.cacheElements();
    this.injectCSS();
    this.setupSidebarEvents();
    this.renderTabs();
    this.showTab(GEMINI_TABS[0].key);
  }
  cacheElements() {
    const s = this.state.sidebar;
    this.els = {
      leftHandle: s.querySelector("#left-resize-handle"),
      closeBtn: s.querySelector("#gemini-review-close"),
      reviewBtn: s.querySelector("#gemini-review-submit"),
      tabsBar: s.querySelector("#gemini-tabs-bar"),
      tabsBarWrap: s.querySelector("#gemini-tabs-bar-wrap"),
      tabContent: s.querySelector("#gemini-tab-content"),
      progressDiv: s.querySelector("#gemini-review-progress"),
      exportArea: s.querySelector("#gemini-export-area")
    };
  }
  injectCSS() {
    if (document.getElementById("gemini-review-css")) return;
    const styleTag = document.createElement("style");
    styleTag.id = "gemini-review-css";
    styleTag.textContent = `
      #gemini-review-sidebar { display:flex; flex-direction:column; height:92vh; }
      #gemini-review-sidebar .gemini-review-header {
        display:flex; justify-content:space-between; align-items:center;
        padding:11px 16px 10px 16px; border-bottom:1px solid #eee; background:#f7f7fa; border-radius:13px 13px 0 0;
      }
      #gemini-review-sidebar .gemini-title { font-weight: bold; font-size: 1.125rem; color: #3276e3;}
      #gemini-review-close { background:#f2f2f2;border:none;color:#444;font-size:1.3em;cursor:pointer;padding:0 0.46em;border-radius:8px;}
      #gemini-review-close:hover { background:#e0e3eb;}
      .gemini-tab-btn {min-width:67px;}
      .gemini-tab-btn.active { background:#fff !important; border-bottom:2px solid #3276e3 !important;}
      #gemini-review-progress { margin-top:14px; margin-left:14px; margin-right:14px;}
      .step-row { display:flex; align-items:center; gap:10px; font-size:1.09em; margin-bottom:0px; padding:3px 0;}
      .step-spinner { width:18px; height:18px; display:inline-block; border:3px solid #b8dcf8; border-top:3px solid #25aecd; border-radius:50%; animation:spin 0.9s linear infinite; margin-right:3px; vertical-align:middle;}
      @keyframes spin {100% {transform:rotate(360deg);} }
      .step-done {color:#1bcb25;font-weight:bold;font-size:1.25em;margin-right:-3px;}
      .step-timer {font-size: 0.96em;color:#888;margin-left:6px;}
      #left-resize-handle {
        position:absolute;left:0;top:0;width:16px;height:100%;cursor:ew-resize;z-index:11001;display:flex;align-items:center;background:transparent;
      }
      #left-resize-handle::after {
        content:'';width:6px;height:54px;min-height:54px;background:#e7ecf1;border-radius:8px;margin-left:3px;margin-top:16px;opacity:0.7;display:block;transition:background 0.18s;
      }
      #left-resize-handle:hover::after {
        background:#abd9f2;opacity:0.93;
      }
      #gemini-tabs-bar-wrap {
        overflow-x:auto !important;
        overflow-y:hidden;
        background:#fff;
        border-radius:9px 9px 0 0;
        scrollbar-width:thin;min-height:38px;max-width:85vw;
      }
      #gemini-tabs-bar {display:flex;min-width:320px;white-space:nowrap;}
      #gemini-tabs-bar::-webkit-scrollbar,
      #gemini-tabs-bar-wrap::-webkit-scrollbar {height:8px;background:#e2e7f3;}
      #gemini-tabs-bar::-webkit-scrollbar-thumb,
      #gemini-tabs-bar-wrap::-webkit-scrollbar-thumb {background:#bad1ed;border-radius:7px;}
      #gemini-tab-content {
        flex:1 1 auto !important; min-height:120px;
        max-height:45vh; overflow-y:auto !important;
        margin:0 14px 0 14px; padding:18px;
        background:#fafbfc; border-radius:10px;
        border:1px solid #eee; box-shadow:0 2px 8px 0 #f0f0f4;
      }
      #gemini-review-submit { background:${THEME.colorMain};color:#fff;font-weight:700;border:none;border-radius:7px;font-size:1.1em;padding:11px 27px;margin:22px auto 0 auto;display:block;cursor:pointer;box-shadow:0 2px 8px -2px #35b68147;}
      #gemini-review-submit:hover { background:${THEME.colorMainHover}; }
      #gemini-export-area { min-height:44px;display:flex;align-items:center;justify-content:flex-end; }
    `;
    document.head.appendChild(styleTag);
  }
  setupSidebarEvents() {
    // Resize handle
    let { leftHandle } = this.els;
    let sidebar = this.state.sidebar;
    let isDragging = false, startX = 0, startW = 0;
    leftHandle.addEventListener('mousedown', e => {
      isDragging = true; startX = e.clientX; startW = sidebar.offsetWidth;
      document.body.style.userSelect = 'none'; e.preventDefault();
    });
    window.addEventListener('mousemove', e => {
      if (!isDragging) return;
      const delta = startX - e.clientX;
      let newWidth = Math.max(340, Math.min(window.innerWidth - 40, startW + delta));
      sidebar.style.width = newWidth + "px";
    });
    window.addEventListener('mouseup', () => {
      if (isDragging) { document.body.style.userSelect = ''; isDragging = false; }
    });
    
    // Close handler
    this.els.closeBtn.onclick = () => { sidebar.style.display = "none"; };
    // Review handler
    this.els.reviewBtn.onclick = () => this.handleReview();
  }
  renderTabs() {
    this.els.tabsBar.innerHTML = "";
    GEMINI_TABS.forEach((tab, i) => {
      const tbtn = document.createElement("button");
      tbtn.className = "gemini-tab-btn";
      tbtn.textContent = tab.name;
      tbtn.setAttribute("data-tab", tab.key);
      tbtn.onclick = () => this.showTab(tab.key);
      tbtn.style = `
        background: #f3f6fa; color: #3276e3; font-weight: 600;
        border: none; border-radius:9px 9px 0 0;
        padding:8px 14px; margin-bottom:-2px;
        cursor:pointer; font-size:1em;outline:none; border-bottom:2px solid #eee; transition:background 0.15s;
      `;
      if (i === 0) tbtn.style.background = "#fff";
      this.els.tabsBar.appendChild(tbtn);
    });
  }
  showTab(tabKey) {
    const { tabsBar, tabContent } = this.els;
    Array.from(tabsBar.children).forEach(btn => {
      btn.className = 'gemini-tab-btn' + (btn.getAttribute('data-tab') === tabKey ? ' active' : '');
      btn.style.background = btn.getAttribute('data-tab') === tabKey ? '#fff' : '#f3f6fa';
      btn.style.borderBottom = btn.getAttribute('data-tab') === tabKey ? '2px solid #3276e3' : '2px solid #eee';
    });
    tabContent.innerHTML = this.state.tabResults && this.state.tabResults[tabKey]
      ? this.state.tabResults[tabKey]
      : `<div style="margin-top:16px; color:#aaa; font-size:1.12em;"><b>Loading...</b></div>`;
  }
  async handleReview() {
    const ext = getGitHubFileExtension();
    const code = getGitHubSourceCode();
    if (!ext || !code) {
      this.els.tabContent.textContent = "Cannot detect file type or code.";
      return;
    }
    this.els.tabContent.innerHTML = "";
    this.els.progressDiv.innerHTML = "";
    this.els.exportArea.innerHTML = "";
    this.state.tabResults = {};
    this.state.tabRawMarkdown = {};
    this.showTab(GEMINI_TABS[0].key);
    Array.from(this.els.tabsBar.children).forEach((btn, idx) => {
      btn.style.background = idx === 0 ? "#fff" : "#f3f6fa";
    });
    chrome.storage.sync.get(['gemini_api_key'], async (result) => {
      const apiKey = result.gemini_api_key;
      if (!apiKey) {
        this.els.tabContent.textContent = "Gemini API key not set.";
        return;
      }
      await this.runGeminiTabsChain(ext, code, apiKey);
    });
  }
  async runGeminiTabsChain(ext, code, apiKey) {
    const tabResults = {};
    const tabRawMarkdown = {};
    const progressDiv = this.els.progressDiv;
    progressDiv.innerHTML = GEMINI_TABS.map(tab =>
      `<div class="step-row" id="step-row-${tab.key}">
        <span class="step-spinner" id="spinner-${tab.key}"></span>
        <span id="step-label-${tab.key}">${tab.name}</span>
        <span class="step-timer" id="step-timer-${tab.key}"></span>
      </div>`).join('');
    // Parallel for first 3
    const firstThree = GEMINI_TABS.slice(0, 3);
    await Promise.all(firstThree.map(async tab => {
      const t0 = performance.now();
      const reply = await callGeminiAPI(buildPrompt(tab.key, ext, code), apiKey);
      const t1 = performance.now();
      const seconds = ((t1 - t0) / 1000).toFixed(2);
      document.getElementById(`step-timer-${tab.key}`).textContent = `(${seconds}s)`;
      document.getElementById(`spinner-${tab.key}`).style.display = "none";
      document.getElementById(`step-row-${tab.key}`).insertAdjacentHTML("afterbegin", `<span class="step-done">✅</span>`);
      document.getElementById(`step-label-${tab.key}`).style.fontWeight = "bold";
      document.getElementById(`step-timer-${tab.key}`).style.color = "#139c13";
      tabResults[tab.key] = `<div style="margin-top:10px;margin-bottom:8px;padding:7px 10px;background:#f9fbff;border-radius:7px;box-shadow:0 0 4px #e0eaff;">
        <h2 style="margin-bottom:11px;color:#267bdb">${tab.name}</h2>
        ${marked.parse(reply)}
        </div>`;
      tabRawMarkdown[tab.key] = reply;
      if (tab.key === GEMINI_TABS[0].key) this.els.tabContent.innerHTML = tabResults[tab.key];
    }));
    // Summary last
    const summaryTab = GEMINI_TABS[3];
    const t0 = performance.now();
    const reply = await callGeminiAPI(buildPrompt(summaryTab.key, ext, code), apiKey);
    const t1 = performance.now();
    const seconds = ((t1 - t0) / 1000).toFixed(2);
    document.getElementById(`step-timer-${summaryTab.key}`).textContent = `(${seconds}s)`;
    document.getElementById(`spinner-${summaryTab.key}`).style.display = "none";
    document.getElementById(`step-row-${summaryTab.key}`).insertAdjacentHTML("afterbegin", `<span class="step-done">✅</span>`);
    document.getElementById(`step-label-${summaryTab.key}`).style.fontWeight = "bold";
    document.getElementById(`step-timer-${summaryTab.key}`).style.color = "#139c13";
    tabResults[summaryTab.key] = `<div style="margin-top:10px;margin-bottom:8px;padding:7px 10px;background:#f9fbff;border-radius:7px;box-shadow:0 0 4px #e0eaff;">
      <h2 style="margin-bottom:11px;color:#267bdb">${summaryTab.name}</h2>
      ${marked.parse(reply)}
      </div>`;
    tabRawMarkdown[summaryTab.key] = reply;
    progressDiv.innerHTML += `<div style="margin-top:12px;color:green;font-size:1.08em;"><b>All reviews completed!</b></div>`;
    this.state.tabResults = tabResults;
    this.state.tabRawMarkdown = tabRawMarkdown;
    this.renderExportButton();
  }
  renderExportButton() {
    const div = this.els.exportArea;
    div.innerHTML = `<button id="gemini-export-btn" style="background:#f7f7fa;border:1px solid #bad1ed;color:#2988e2;border-radius:8px;font-size:1em;padding:9px 20px;cursor:pointer;box-shadow:0 2px 5px -2px #e7ecfa;float:right;margin:9px 24px 0 0;">Export</button>`;
    div.querySelector("#gemini-export-btn").onclick = () => this.handleExport();
  }
  handleExport() {
    const exportType = prompt(
      "Export type:\n1 = TXT (all tabs)\n2 = PDF (all tabs)\n3 = Markdown (.md for all tabs)\n\n(Type 1, 2, or 3 then OK)"
    );
    if (!exportType) return;
    let txtContent = "", htmlContent = "", mdContent = "";
    for (let tab of GEMINI_TABS) {
      let tabHtml = this.state.tabResults[tab.key] || "";
      let tmp = document.createElement("div"); tmp.innerHTML = tabHtml;
      let plain = tmp.innerText || tmp.textContent || "";
      txtContent += `--- ${tab.name} ---\n${plain}\n\n`;
      htmlContent += `<h2>${tab.name}</h2>\n${tabHtml}\n<hr>`;
      let rawMd = this.state.tabRawMarkdown[tab.key] || plain;
      mdContent += `## ${tab.name}\n\n${rawMd}\n\n`;
    }
    txtContent += `\nExported from Gemini Chrome Plugin, ${new Date().toLocaleString()}\n`;
    mdContent += `\n_Exported from Gemini Chrome Plugin, ${new Date().toLocaleString()}_\n`;
    htmlContent += `<footer><small>Exported from Gemini Chrome Plugin, ${new Date().toLocaleString()}</small></footer>`;
    if (exportType === "1") { // TXT
      let fileName = "gemini-code-review.txt";
      let blob = new Blob([txtContent], { type: "text/plain" });
      this.saveBlob(blob, fileName);
    } else if (exportType === "2") { // PDF: via browser print
      let printWindow = window.open('', '', 'width=900,height=1000');
      printWindow.document.write(`
        <html><head><title>Gemini Code Review Export</title>
        <style>body { font-family:Segoe UI,Arial,sans-serif;padding:25px;font-size:15px;}
         h2 { color: #267bdb; } code, pre { background:#f4f2fa;border-radius:4px;padding:7px;}
         div { margin-bottom:17px; }</style>
         </head><body><h1>All Gemini Code Reviews</h1>${htmlContent}</body></html>`);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    } else if (exportType === "3") { // Markdown
      let fileName = "gemini-code-review.md";
      let blob = new Blob([mdContent], { type: "text/markdown" });
      this.saveBlob(blob, fileName);
    } else {
      alert("Export type not recognized.");
    }
  }
  saveBlob(blob, fileName) {
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url; a.download = fileName; document.body.appendChild(a);
    a.click(); document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 999);
  }
}

// LOGIC
function buildPrompt(tabKey, ext, code) {
  if (tabKey === "style") {
    return `Review this ${ext} code for style/readability. Formatting, conventions, naming, idioms, best practices. Markdown, sections for strengths & weaknesses.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``;
  }
  if (tabKey === "bugs") {
    return `Analyze for bugs, logic errors, edge cases, failure points. List problems and fixes. Markdown.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``;
  }
  if (tabKey === "tests") {
    return `Suggest unit/integration test cases for this ${ext} code. Provide code snippets where possible. Markdown.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``;
  }
  if (tabKey === "summary") {
    return `Summarize what this ${ext} code does. Concise, markdown.\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``;
  }
  return `Review code:\n\n\`\`\`${ext.slice(1)}\n${code}\n\`\`\``;
}
async function callGeminiAPI(prompt, apiKey) {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_API_MODEL}:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
      }
    );
    const data = await response.json();
    if (
      data && data.candidates && data.candidates[0] &&
      data.candidates[0].content && data.candidates[0].content.parts[0]
    ) {
      return data.candidates[0].content.parts[0].text;
    }
    return "No response from Gemini.";
  } catch(e) {
    return "Error: " + e;
  }
}

// ===== BOOTSTRAP =====
if (isSupportedFilePage()) {
  window.geminiReviewUI = new GeminiReviewUI();
}