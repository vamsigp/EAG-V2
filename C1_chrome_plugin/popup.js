function formatBytes(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024*1024)).toFixed(1) + " MB";
}

async function getCurrentTab() {
  let [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  return tab;
}

// Get redirect chain
async function showRedirects(tab) {
  chrome.runtime.sendMessage({type: "getRedirects", tabId: tab.id}, function(response) {
    let div = document.getElementById("redirects");
    if (!response || !response.redirects || response.redirects.length === 0) {
      div.textContent = "No redirects detected for this tab session.";
    } else {
      let html = "<ol>";
      for (let url of response.redirects) html += `<li><code>${url}</code></li>`;
      html += "</ol>";
      div.innerHTML = html;
    }
  });
}

// Get cookies and show size/expiration
async function showCookies(tab) {
  let url = tab.url;
  let domain;
  try {
    domain = (new URL(url)).hostname;
  } catch { return; }

  chrome.cookies.getAll({domain}, function(cookies) {
    let div = document.getElementById("cookies");
    if (!cookies || cookies.length === 0) {
      div.textContent = "No cookies for this domain.";
      return;
    }
    let rows = cookies.map(cookie => {
      let valSize = encodeURIComponent(cookie.value).length;
      let expires = cookie.expirationDate ? 
        (new Date(cookie.expirationDate * 1000)).toLocaleString() : 
        "-";
      return `<tr>
        <td>${cookie.name}</td>
        <td>${formatBytes(valSize)}</td>
        <td>${expires}</td>
      </tr>`;
    });
    div.innerHTML = `<table>
      <tr><th>Name</th><th>Value Size</th><th>Expires</th></tr>
      ${rows.join("\n")}
    </table>`;
  });
}

// Main
getCurrentTab().then(tab => {
  showRedirects(tab);
  showCookies(tab);
});