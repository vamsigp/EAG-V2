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
    div.textContent = formatBytes((resp && resp.bandwidth) || 0);
  });
}

function showRedirects(tabId) {
  chrome.runtime.sendMessage({ type: "getTabData", tabId }, (resp) => {
    let div = document.getElementById("redirects");
    let redirects = (resp && resp.redirects) || [];
    if (!redirects.length) {
      div.textContent = "No redirects detected for this tab session.";
    } else {
      let html = "<ol>" + redirects.map(url => `<li><code>${url}</code></li>`).join('') + "</ol>";
      div.innerHTML = html;
    }
  });
}

function showCookies(tab) {
  let url = tab.url;
  let domain;
  try {
    domain = (new URL(url)).hostname;
  } catch {
    document.getElementById("cookies").textContent = "Invalid URL";
    return;
  }

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

async function getDNSInfo(hostname) {
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

async function getSSLInfo(hostname) {
  const url = `https://api.ssllabs.com/api/v3/analyze?host=${hostname}&fromCache=on&all=done`;
  try {
    let resp = await fetch(url);
    let data = await resp.json();
    const endpoint = (data.endpoints && data.endpoints.length) ? data.endpoints[0] : null;
    if (!endpoint || !endpoint.details) return null;
    let protocols = endpoint.details.protocols
      .map(p => p.name + (p.version ? (" " + p.version) : ""))
      .join(', ');
    let ciphers = endpoint.details.suites
      .map(s => `${s.name}${s.q === 1 ? ' (default)' : ''}`)
      .join(', ');
    return {
      tlsVersion: protocols,
      ciphers: ciphers
    };
  } catch (e) {
    return null;
  }
}

async function showTLS(tab) {
  let url = tab.url;
  let hostname;
  try {
    hostname = (new URL(url)).hostname;
  } catch {
    return;
  }
  let divTLS = document.getElementById("tls");
  divTLS.textContent = 'Resolving...';
  let info = await getSSLInfo(hostname);
  if (!info) {
    divTLS.textContent = 'TLS info not available (site may be private, slow, or blocked for scanning).';
  } else {
    divTLS.innerHTML = `
      <b>TLS Versions Supported:</b> ${info.tlsVersion}<br/>
      <b>Cipher Suites Offered:</b> ${info.ciphers}
    `;
  }
}

function showAnalytics(tab) {
  let div = document.getElementById("analytics");
  chrome.tabs.sendMessage(tab.id, {type: "analytics-check"}, response => {
    if (chrome.runtime.lastError) {
      div.textContent = "(Unable to analyze: permission or access error)";
      return;
    }
    const providers = response && response.providers ? response.providers : [];
    if (!providers.length) {
      div.textContent = "No major analytics providers detected.";
    } else {
      div.innerHTML = `<ul>${providers.map(p => `<li>${p}</li>`).join('')}</ul>`;
    }
  });
}

getCurrentTab().then(tab => {
  showBandwidth(tab.id);
  showRedirects(tab.id);
  showCookies(tab);
  showDNS(tab);
  showTLS(tab);
  showAnalytics(tab);
});