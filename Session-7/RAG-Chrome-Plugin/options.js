// Options page JavaScript
document.addEventListener('DOMContentLoaded', async () => {
    // Default excluded domains
    const DEFAULT_DOMAINS = [
        'mail.google.com',
        'gmail.com',
        'web.whatsapp.com',
        'accounts.google.com',
        'login.microsoftonline.com',
        'github.com/login',
        'paypal.com',
        'stripe.com'
    ];

    // Default settings
    const DEFAULT_SETTINGS = {
        customExcludedDomains: [],
        minContentLength: 200,
        maxContentLength: 10000,
        processingDelay: 2,
        enableSPADetection: true,
        maxIndexSize: 1000,
        enableAutoCleanup: true
    };

    let currentSettings = { ...DEFAULT_SETTINGS };

    // DOM elements
    const domainInput = document.getElementById('domainInput');
    const addDomainBtn = document.getElementById('addDomainBtn');
    const defaultDomainsContainer = document.getElementById('defaultDomains');
    const customDomainsContainer = document.getElementById('customDomains');
    const saveBtn = document.getElementById('saveBtn');
    const saveStatus = document.getElementById('saveStatus');
    const exportDataBtn = document.getElementById('exportDataBtn');
    const importDataBtn = document.getElementById('importDataBtn');
    const importFileInput = document.getElementById('importFileInput');
    const clearAllBtn = document.getElementById('clearAllBtn');

    // Setting inputs
    const minContentLengthInput = document.getElementById('minContentLength');
    const maxContentLengthInput = document.getElementById('maxContentLength');
    const processingDelayInput = document.getElementById('processingDelay');
    const enableSPADetectionInput = document.getElementById('enableSPADetection');
    const maxIndexSizeInput = document.getElementById('maxIndexSize');
    const enableAutoCleanupInput = document.getElementById('enableAutoCleanup');

    // Stats elements
    const totalPagesSpan = document.getElementById('totalPages');
    const storageUsedSpan = document.getElementById('storageUsed');
    const modelStatusSpan = document.getElementById('modelStatus');

    // Initialize
    await loadSettings();
    await loadStats();
    renderDomains();
    updateSettingsUI();

    // Event listeners
    addDomainBtn.addEventListener('click', addCustomDomain);
    domainInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addCustomDomain();
        }
    });

    saveBtn.addEventListener('click', saveSettings);
    exportDataBtn.addEventListener('click', exportData);
    importDataBtn.addEventListener('click', () => importFileInput.click());
    importFileInput.addEventListener('change', importData);
    clearAllBtn.addEventListener('click', clearAllData);

    // Settings input listeners
    [minContentLengthInput, maxContentLengthInput, processingDelayInput,
        enableSPADetectionInput, maxIndexSizeInput, enableAutoCleanupInput].forEach(input => {
            input.addEventListener('change', updateSettingsFromUI);
        });

    async function loadSettings() {
        try {
            const result = await chrome.storage.sync.get(['ragIndexerSettings']);
            if (result.ragIndexerSettings) {
                currentSettings = { ...DEFAULT_SETTINGS, ...result.ragIndexerSettings };
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    async function saveSettings() {
        try {
            await chrome.storage.sync.set({ ragIndexerSettings: currentSettings });
            showSaveStatus('Settings saved successfully', 'success');
        } catch (error) {
            console.error('Failed to save settings:', error);
            showSaveStatus('Failed to save settings', 'error');
        }
    }

    async function loadStats() {
        try {
            const response = await chrome.runtime.sendMessage({ action: 'getStats' });
            if (response.success) {
                const stats = response.stats;
                totalPagesSpan.textContent = stats.totalEntries;
                modelStatusSpan.textContent = stats.modelLoaded ? '✅ Loaded' : '⏳ Loading...';

                // Estimate storage usage (rough calculation)
                const estimatedSize = Math.round(stats.totalEntries * 5); // ~5KB per entry
                storageUsedSpan.textContent = estimatedSize > 1024 ?
                    `${Math.round(estimatedSize / 1024)} MB` : `${estimatedSize} KB`;
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    function renderDomains() {
        // Render default domains
        defaultDomainsContainer.innerHTML = DEFAULT_DOMAINS.map(domain =>
            `<div class="domain-tag default">${domain}</div>`
        ).join('');

        // Render custom domains
        customDomainsContainer.innerHTML = currentSettings.customExcludedDomains.map(domain =>
            `<div class="domain-tag">
                ${domain}
                <button class="remove-btn" onclick="removeCustomDomain('${domain}')">×</button>
            </div>`
        ).join('');
    }

    function addCustomDomain() {
        const domain = domainInput.value.trim().toLowerCase();
        if (!domain) return;

        // Validate domain format
        if (!/^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])*$/.test(domain)) {
            alert('Please enter a valid domain name');
            return;
        }

        // Check if already exists
        if (DEFAULT_DOMAINS.includes(domain) || currentSettings.customExcludedDomains.includes(domain)) {
            alert('Domain already exists in the exclusion list');
            return;
        }

        currentSettings.customExcludedDomains.push(domain);
        domainInput.value = '';
        renderDomains();
    }

    // Make this function global so it can be called from inline onclick
    window.removeCustomDomain = function (domain) {
        currentSettings.customExcludedDomains = currentSettings.customExcludedDomains.filter(d => d !== domain);
        renderDomains();
    };

    function updateSettingsUI() {
        minContentLengthInput.value = currentSettings.minContentLength;
        maxContentLengthInput.value = currentSettings.maxContentLength;
        processingDelayInput.value = currentSettings.processingDelay;
        enableSPADetectionInput.checked = currentSettings.enableSPADetection;
        maxIndexSizeInput.value = currentSettings.maxIndexSize;
        enableAutoCleanupInput.checked = currentSettings.enableAutoCleanup;
    }

    function updateSettingsFromUI() {
        currentSettings.minContentLength = parseInt(minContentLengthInput.value);
        currentSettings.maxContentLength = parseInt(maxContentLengthInput.value);
        currentSettings.processingDelay = parseInt(processingDelayInput.value);
        currentSettings.enableSPADetection = enableSPADetectionInput.checked;
        currentSettings.maxIndexSize = parseInt(maxIndexSizeInput.value);
        currentSettings.enableAutoCleanup = enableAutoCleanupInput.checked;
    }

    async function exportData() {
        try {
            const data = await chrome.storage.local.get(null);
            const exportData = {
                version: '1.0.0',
                timestamp: Date.now(),
                settings: currentSettings,
                data: data
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `rag-indexer-backup-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);

            showSaveStatus('Data exported successfully', 'success');
        } catch (error) {
            console.error('Export failed:', error);
            showSaveStatus('Export failed', 'error');
        }
    }

    async function importData() {
        const file = importFileInput.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const importData = JSON.parse(text);

            if (!importData.version || !importData.data) {
                throw new Error('Invalid backup file format');
            }

            if (confirm('This will replace all current data. Are you sure?')) {
                // Clear existing data
                await chrome.storage.local.clear();

                // Import data
                await chrome.storage.local.set(importData.data);

                // Import settings
                if (importData.settings) {
                    currentSettings = { ...DEFAULT_SETTINGS, ...importData.settings };
                    await saveSettings();
                    updateSettingsUI();
                    renderDomains();
                }

                // Refresh stats
                await loadStats();

                showSaveStatus('Data imported successfully', 'success');
            }
        } catch (error) {
            console.error('Import failed:', error);
            showSaveStatus('Import failed: ' + error.message, 'error');
        }

        importFileInput.value = '';
    }

    async function clearAllData() {
        if (!confirm('Are you sure you want to delete ALL indexed data and settings? This cannot be undone!')) {
            return;
        }

        if (!confirm('This is your final warning. All data will be permanently deleted. Continue?')) {
            return;
        }

        try {
            // Clear all data
            await chrome.storage.local.clear();
            await chrome.storage.sync.clear();

            // Reset to defaults
            currentSettings = { ...DEFAULT_SETTINGS };
            updateSettingsUI();
            renderDomains();

            // Refresh stats
            await loadStats();

            // Notify background script
            chrome.runtime.sendMessage({ action: 'clearIndex' });

            showSaveStatus('All data cleared successfully', 'success');
        } catch (error) {
            console.error('Clear all failed:', error);
            showSaveStatus('Failed to clear data', 'error');
        }
    }

    function showSaveStatus(message, type) {
        saveStatus.textContent = message;
        saveStatus.className = `save-status ${type}`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = 'save-status';
        }, 3000);
    }
});