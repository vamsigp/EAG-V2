(function() {
  const PROVIDERS = [
    {
      name: "Google Analytics",
      patterns: [
        /www\.google-analytics\.com/,
        /analytics\.js/,
        /gtag\./,
        /ga\./,
        /UA-\d{4,10}-\d+/,
      ],
      globals: ["ga", "gtag"]
    },
    {
      name: "Google Tag Manager",
      patterns: [
        /www\.googletagmanager\.com/,
        /GTM-[A-Z0-9]+/,
      ]
    },
    {
      name: "Facebook Pixel",
      patterns: [
        /connect\.facebook\.net/,
        /fbq\./,
      ],
      globals: ["fbq"]
    },
    {
      name: "Hotjar",
      patterns: [
        /static\.hotjar\.com/,
        /hotjar\.com/,
        /hjid/,
      ],
      globals: ["hj"]
    },
    {
      name: "Adobe Analytics",
      patterns: [
        /omtrdc\.net/,
        /adobedc\.net/,
        /satellite/,
        /s_code\.js/,
      ]
    },
    {
      name: "Mixpanel",
      patterns: [
        /cdn\.mixpanel\.com/,
        /mixpanel\./,
      ],
      globals: ["mixpanel"]
    },
    {
      name: "Segment",
      patterns: [
        /cdn\.segment\.com/,
        /analytics\.js/,
      ],
      globals: ["analytics"]
    },
    {
      name: "Matomo (Piwik)",
      patterns: [
        /matomo\.js/,
        /piwik\.js/
      ],
      globals: ["_paq"]
    }
  ];

  function detectAnalytics() {
    const found = [];
    const scripts = Array.from(document.getElementsByTagName('script'));
    const html = document.documentElement.innerHTML;
    for (const provider of PROVIDERS) {
      let detected = false;
      // Scan script src attributes
      for (const script of scripts) {
        if (script.src) {
          for (const pat of provider.patterns) {
            if (pat.test(script.src)) {
              detected = true;
              break;
            }
          }
        }
        if (detected) break;
      }
      // Scan inline script contents and page HTML
      if (!detected && provider.patterns) {
        for (const pat of provider.patterns) {
          if (pat.test(html)) {
            detected = true;
            break;
          }
        }
      }
      // Check for global variables
      if (!detected && provider.globals) {
        for (const g of provider.globals) {
          if (typeof window[g] !== "undefined") {
            detected = true;
            break;
          }
        }
      }
      if (detected) found.push(provider.name);
    }
    return found;
  }

  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg && msg.type === "analytics-check") {
      const results = detectAnalytics();
      sendResponse({ providers: results });
    }
  });
})();