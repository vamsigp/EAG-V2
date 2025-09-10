# URL Redirects & Cookies & Analytics Analyzer Chrome Extension

Hello and welcome! 👋

This Chrome extension was created for anyone curious about what’s under the hood when they browse a web page.

With one click, you can peek behind the scenes: see what cookies the site stores, how much bandwidth the page consumed, which analytics services are tracking you, and so much more!

## 🌟 Features

### Redirect Chain Visualization:

See each hop (redirect) your browser took before arriving at the final page.

### Cookie Audit:

Get a comprehensive table of all cookies set for the current site (name, size, and expiry).

### Bandwidth Consumption:

Find out the total bytes your browser downloaded to render the current page.

### IP Address & CNAME Resolution:

Easily see the server’s IP and any CNAME chains using DNS-over-HTTPS.

### TLS Info (via SSL Labs):

View the TLS protocol versions and cipher suites the site offers to browsers, for public hosts.

### Real-Time Analytics Provider Detection:

Discover which major analytics or tracker services (Google Analytics, Facebook Pixel, Hotjar, etc.) are loaded on the page.

## 🔧 How Does It Work?

Everything happens locally in your browser, powered by Chrome’s extensions APIs:

webRequest tracks redirects and bandwidth.
cookies API audits site cookies.
DNS-over-HTTPS fetches IP and CNAME info.
TLS/cipher info pulled from SSL Labs (for public sites only).
A smart content script looks for analytics by scanning the DOM (script URLs, global JS variables, and more).

## 🤝 Assumptions

### Browser Security:
Chrome does not expose direct TLS handshake info or certificate details to extensions for safety. TLS details are fetched from an external source (SSL Labs) when possible.
### Content Script Scope:
The analytics detector runs on all standard web pages, but not on Chrome’s own pages (chrome://), the Web Store, or incognito pages unless the extension is enabled for them.
### Bandwidth Reporting:
Is an estimate. Some resources (like compressed or chunked content) may not report full content-length, so the number may be lower than total bytes received.
### Cookies:
Only cookies for the current site’s domain are displayed.
### Permissions:
The extension requests broad permissions, but only for the features you see.
### DNS and SSL Labs APIs:
External requests are required to resolve DNS info and TLS/ciphers — for intranet/private or firewall-blocked hosts, these features may not display results.

## 🚀 How To Use

- Download or clone this repository.
- Go to chrome://extensions in your browser.
- Enable Developer mode.
- Click “Load unpacked” and select the project folder.
- Visit any website, click the extension icon, and explore the data!


## 🔮 Possible Future Enhancements

### Tracker and Ad Network Detection:

Expand the content script's intelligence to identify a wider array of ad-tech companies, fingerprinting scripts, and social media trackers.

### Security Header Analyzer:

Show which security headers (Content-Security-Policy, Strict-Transport-Security, etc.) a site sends.

### SEO and Accessibility Insights:

Check meta tags, title, heading structure, and accessibility features (alt text, ARIA).

### Page Performance Metrics:

Surface navigation and resource timing stats (DOMContentLoaded, load, etc.).

### Detect Use of Modern Web Features:

Service Workers, PWA manifests, WebAssembly usage, etc.

### Export/Share Analysis:

Output reports to CSV or PDF for audit/sharing.

### Customization:

Let users choose which fields or sections to display in the popup.

### Per-Resource Audit:

Drill down resource by resource for cookies, bandwidth, tracker, and security.

## 🙏 Thanks & Feedback

Thank you for using this extension!

If you have ideas, want to suggest a new detection, or notice something that could be done better, please open an issue — or just say hello. Contributions and feedback always welcome.

Happy browsing! ✨

I made this to help the curious — privacy nerds, SEOs, web devs, or anyone just wondering: “What happens when I load this page?”

Cheers!

Note: Much of this project was crafted through "vibe coding" — thoughtful improvisation and creative exploration rather than strictly following a traditional spec.
