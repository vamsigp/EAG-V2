function formatBytes(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024*1024)).toFixed(1) + " MB";
}

async function getCurrentTab() {
  let [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  return tab;
}

function showBandwidth(tabId) {
  chrome.runtime.sendMessage({ type: "getTabData", tabId }, (resp) => {
    let div = document.getElementById("bandwidth");
    div.textContent = formatBytes(resp.bandwidth || 0);
  });
}

function showRedirects(tabId) {
  chrome.runtime.sendMessage({ type: "getTabData", tabId }, (resp) => {
    let div = document.getElementById("redirects");
    let redirects = resp.redirects || [];
    if (!redirects.length) {
      div.textContent = "No redirects detected for this tab session.";
    } else {
      let html = "<ol>";
      for (let url of redirects) html += `<li><code>${url}</code></li>`;
      html += "</ol>";
      div.innerHTML = html;
    }
  });
}

function showCookies(tab) {
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

// Get IP and CNAME via a DNS over HTTPS API
async function getDNSInfo(hostname) {
  // Google DNS over HTTPS API
  const url = `https://dns.google.com/resolve?name=${hostname}&type=ANY`;
  try {
    let resp = await fetch(url);
    let data = await resp.json();
    let ip = "", cnames = [];
    if (data.Answer && Array.isArray(data.Answer)) {
      for (let ans of data.Answer) {
        if (ans.type === 1) { // A record
          ip = ans.data;
        } else if (ans.type === 5) { // CNAME
          cnames.push(ans.data);
        }
      }
    }
    return {ip, cnames};
  } catch {
    return {ip: "", cnames: []};
  }
}

async function showDNS(tab) {
  let url = tab.url;
  let hostname;
  try {
    hostname = (new URL(url)).hostname;
  } catch {
    return;
  }
  let divIp = document.getElementById("ip");
  let divCname = document.getElementById("cnames");
  divIp.textContent = 'Resolving...';
  divCname.textContent = 'Resolving...';
  let dnsInfo = await getDNSInfo(hostname);
  divIp.textContent = dnsInfo.ip ? dnsInfo.ip : '(No A record/IP found)';
  divCname.innerHTML = dnsInfo.cnames.length
    ? `<ul>${dnsInfo.cnames.map(c => `<li><code>${c}</code></li>`).join('')}</ul>`
    : '(No CNAME record found)';
}

// Main
getCurrentTab().then(tab => {
  showBandwidth(tab.id);
  showRedirects(tab.id);
  showCookies(tab);
  showDNS(tab);
});