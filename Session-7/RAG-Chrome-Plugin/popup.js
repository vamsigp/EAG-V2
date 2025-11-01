// Popup JavaScript for RAG Web Indexer
document.addEventListener('DOMContentLoaded', async () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const topKInput = document.getElementById('topK');
    const searchResults = document.getElementById('searchResults');
    const recentPages = document.getElementById('recentPages');
    const indexCount = document.getElementById('indexCount');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const clearIndexBtn = document.getElementById('clearIndex');
    const totalPagesSpan = document.getElementById('totalPages');
    const modelStatusSpan = document.getElementById('modelStatus');

    // Initialize popup
    await loadStats();
    await loadRecentPages();

    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });

    // Search functionality
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Clear index
    clearIndexBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear all indexed data? This cannot be undone.')) {
            await clearIndex();
        }
    });

    function switchTab(tabName) {
        // Update tab buttons
        tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        tabContents.forEach(content => {
            if (content.id === tabName + 'Tab') {
                content.classList.remove('hidden');
            } else {
                content.classList.add('hidden');
            }
        });

        // Load content for specific tabs
        if (tabName === 'recent') {
            loadRecentPages();
        } else if (tabName === 'settings') {
            loadStats();
        }
    }

    async function performSearch() {
        const query = searchInput.value.trim();
        const topK = parseInt(topKInput.value) || 5;

        if (!query) {
            showSearchMessage('Please enter a search query');
            return;
        }

        showSearchMessage('Searching...', 'loading');

        try {
            const response = await chrome.runtime.sendMessage({
                action: 'search',
                query: query,
                topK: topK
            });

            if (response.success && response.results.length > 0) {
                displaySearchResults(response.results);
            } else {
                showSearchMessage('No similar pages found');
            }
        } catch (error) {
            console.error('Search error:', error);
            showSearchMessage('Search failed. Please try again.', 'error');
        }
    }

    async function loadRecentPages() {
        recentPages.innerHTML = '<div class="loading">Loading recent pages...</div>';

        try {
            const response = await chrome.runtime.sendMessage({
                action: 'getRecentPages',
                limit: 10
            });

            if (response.success && response.pages.length > 0) {
                displayPages(response.pages, recentPages);
            } else {
                recentPages.innerHTML = '<div class="no-results">No pages indexed yet</div>';
            }
        } catch (error) {
            console.error('Failed to load recent pages:', error);
            recentPages.innerHTML = '<div class="error">Failed to load recent pages</div>';
        }
    }

    async function loadStats() {
        try {
            const response = await chrome.runtime.sendMessage({
                action: 'getStats'
            });

            if (response.success) {
                const stats = response.stats;
                indexCount.textContent = stats.totalEntries;
                totalPagesSpan.textContent = stats.totalEntries;
                modelStatusSpan.textContent = stats.modelLoaded ? '✅ Loaded' : '⏳ Loading...';
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    async function clearIndex() {
        try {
            const response = await chrome.runtime.sendMessage({
                action: 'clearIndex'
            });

            if (response.success) {
                await loadStats();
                await loadRecentPages();
                searchResults.innerHTML = '<div class="no-results">Enter a search query to find similar pages</div>';
                alert('Index cleared successfully');
            } else {
                alert('Failed to clear index');
            }
        } catch (error) {
            console.error('Failed to clear index:', error);
            alert('Failed to clear index');
        }
    }

    function displaySearchResults(results) {
        displayPages(results, searchResults);
    }

    function displayPages(pages, container) {
        if (pages.length === 0) {
            container.innerHTML = '<div class="no-results">No pages found</div>';
            return;
        }

        const html = pages.map(page => createPageHTML(page)).join('');
        container.innerHTML = html;

        // Add click handlers to open URLs
        container.querySelectorAll('.page-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                chrome.tabs.create({ url: pages[index].metadata.url });
            });
        });
    }

    function createPageHTML(page) {
        const similarity = page.similarity ? Math.round(page.similarity * 100) : null;
        const timestamp = new Date(page.timestamp).toLocaleDateString();

        return `
            <div class="page-item">
                <div class="page-title">${escapeHtml(page.metadata.title || 'Untitled')}</div>
                <div class="page-url">${escapeHtml(page.metadata.url)}</div>
                <div class="page-content">${escapeHtml(page.content || page.metadata.description || '')}</div>
                <div class="page-meta">
                    <span class="timestamp">${timestamp}</span>
                    ${similarity !== null ? `<span class="similarity-score">${similarity}%</span>` : ''}
                </div>
            </div>
        `;
    }

    function showSearchMessage(message, type = 'no-results') {
        searchResults.innerHTML = `<div class="${type}">${escapeHtml(message)}</div>`;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});