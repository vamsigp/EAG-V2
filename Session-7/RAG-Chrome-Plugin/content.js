// Content script for extracting page content
(function () {
    'use strict';

    // List of confidential domains to skip
    const CONFIDENTIAL_DOMAINS = [
        'mail.google.com',
        'gmail.com',
        'web.whatsapp.com',
        'accounts.google.com',
        'login.microsoftonline.com',
        'github.com/login',
        'banking',
        'paypal.com',
        'stripe.com'
    ];

    // Check if current domain should be skipped
    function shouldSkipDomain() {
        const hostname = window.location.hostname.toLowerCase();
        const pathname = window.location.pathname.toLowerCase();

        return CONFIDENTIAL_DOMAINS.some(domain =>
            hostname.includes(domain) ||
            pathname.includes('login') ||
            pathname.includes('signin') ||
            pathname.includes('auth')
        );
    }

    // Extract meaningful text content from the page
    function extractPageContent() {
        // Remove script, style, and other non-content elements
        const elementsToRemove = document.querySelectorAll('script, style, nav, header, footer, aside, .advertisement, .ads, .sidebar');
        const clonedDoc = document.cloneNode(true);

        elementsToRemove.forEach(el => {
            const clonedEl = clonedDoc.querySelector(el.tagName);
            if (clonedEl) clonedEl.remove();
        });

        // Get text from main content areas
        const contentSelectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main',
            'body'
        ];

        let content = '';

        for (const selector of contentSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                content = element.innerText || element.textContent || '';
                break;
            }
        }

        // Clean up the content
        content = content
            .replace(/\\s+/g, ' ')  // Replace multiple whitespace with single space
            .replace(/\\n+/g, '\\n') // Replace multiple newlines with single newline
            .trim();

        return content;
    }

    // Get page metadata
    function getPageMetadata() {
        const title = document.title || '';
        const description = document.querySelector('meta[name="description"]')?.content || '';
        const keywords = document.querySelector('meta[name="keywords"]')?.content || '';
        const url = window.location.href;
        const domain = window.location.hostname;

        return {
            title,
            description,
            keywords,
            url,
            domain,
            timestamp: Date.now()
        };
    }

    // Main function to process the page
    function processPage() {
        // Skip if domain is confidential
        if (shouldSkipDomain()) {
            console.log('RAG Indexer: Skipping confidential domain:', window.location.hostname);
            return;
        }

        // Skip if page is too small or seems like a landing page
        const content = extractPageContent();
        if (content.length < 200) {
            console.log('RAG Indexer: Skipping page with insufficient content');
            return;
        }

        const metadata = getPageMetadata();

        // Send content to background script for processing
        chrome.runtime.sendMessage({
            action: 'processPage',
            data: {
                content: content.substring(0, 10000), // Limit content size
                metadata: metadata
            }
        }, (response) => {
            if (response && response.success) {
                console.log('RAG Indexer: Page processed successfully');
            } else {
                console.log('RAG Indexer: Failed to process page');
            }
        });
    }

    // Wait for page to be fully loaded before processing
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(processPage, 2000); // Wait 2 seconds after DOM loaded
        });
    } else {
        setTimeout(processPage, 2000); // Wait 2 seconds if already loaded
    }

    // Listen for navigation changes (for SPAs)
    let lastUrl = window.location.href;
    const observer = new MutationObserver(() => {
        if (window.location.href !== lastUrl) {
            lastUrl = window.location.href;
            setTimeout(processPage, 3000); // Wait longer for SPA content to load
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();