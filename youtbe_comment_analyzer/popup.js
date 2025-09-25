// Popup JavaScript
let analyzedComments = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', async () => {
  await initializePopup();
  setupEventListeners();
});

async function initializePopup() {
  // Check if API key is configured
  const { apiKey } = await chrome.storage.sync.get(['apiKey']);
  
  if (apiKey) {
    document.getElementById('configSection').style.display = 'none';
    document.getElementById('mainContent').style.display = 'block';
    updateStatus('Ready', 'success');
  } else {
    document.getElementById('configSection').style.display = 'block';
    document.getElementById('mainContent').style.display = 'none';
    updateStatus('API key required', 'warning');
  }
}

function setupEventListeners() {
  // API Key configuration
  document.getElementById('saveApiKey').addEventListener('click', saveApiKey);
  document.getElementById('apiKeyInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') saveApiKey();
  });

  // Main actions
  document.getElementById('analyzeBtn').addEventListener('click', analyzeComments);
  document.getElementById('summarizeBtn').addEventListener('click', showSummary);

  // Filter tabs
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      const filter = e.target.dataset.filter;
      setActiveFilter(filter);
      filterComments(filter);
    });
  });

  // Modal controls
  document.getElementById('closeSummary').addEventListener('click', closeSummary);
  document.getElementById('summaryModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeSummary();
  });
}

async function saveApiKey() {
  const apiKey = document.getElementById('apiKeyInput').value.trim();
  
  if (!apiKey) {
    showNotification('Please enter a valid API key', 'error');
    return;
  }

  try {
    await chrome.storage.sync.set({ apiKey });
    showNotification('API key saved successfully!', 'success');
    await initializePopup();
  } catch (error) {
    showNotification('Error saving API key', 'error');
    console.error(error);
  }
}

async function analyzeComments() {
  try {
    updateStatus('Loading comments...', 'loading');
    showLoadingOverlay(true);

    // Get comments from active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.url.includes('youtube.com')) {
      throw new Error('Please navigate to a YouTube video page');
    }

    // Get comments from content script
    const response = await chrome.tabs.sendMessage(tab.id, { action: 'getComments' });
    
    if (!response || !response.comments || response.comments.length === 0) {
      throw new Error('No comments found. Make sure you are on a YouTube video with comments.');
    }

    updateStatus('Analyzing with AI...', 'loading');

    // Send comments to background script for analysis
    const analysis = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: 'analyzeComments', comments: response.comments },
        (response) => {
          if (response.error) {
            reject(new Error(response.error));
          } else {
            resolve(response.analysis);
          }
        }
      );
    });

    analyzedComments = analysis;
    displayComments(analyzedComments);
    updateCounts();
    
    document.getElementById('filterTabs').style.display = 'block';
    document.getElementById('summarizeBtn').disabled = false;
    
    updateStatus(`Analyzed ${analyzedComments.length} comments`, 'success');
    showNotification('Comments analyzed successfully!', 'success');

  } catch (error) {
    console.error('Error analyzing comments:', error);
    updateStatus('Error', 'error');
    showNotification(error.message, 'error');
  } finally {
    showLoadingOverlay(false);
  }
}

function displayComments(comments) {
  console.log('🎯 Displaying comments with filter:', currentFilter);
  const container = document.getElementById('commentsContainer');
  const placeholder = document.getElementById('placeholder');
  
  if (comments.length === 0) {
    placeholder.style.display = 'block';
    container.innerHTML = '';
    return;
  }

  placeholder.style.display = 'none';
  
  const filteredComments = currentFilter === 'all' 
    ? comments 
    : comments.filter(comment => {
        const matches = comment.category === currentFilter;
        console.log(`Comment "${comment.text.substring(0, 30)}..." category: "${comment.category}" matches filter "${currentFilter}": ${matches}`);
        return matches;
      });

  console.log(`📊 Filtered ${filteredComments.length} out of ${comments.length} comments`);

  if (filteredComments.length === 0) {
    container.innerHTML = `
      <div class="no-results">
        <p>No ${currentFilter.toLowerCase()} comments found.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filteredComments.map((comment, index) => `
    <div class="comment-item ${comment.category.toLowerCase()}" data-category="${comment.category}">
      <div class="comment-header">
        <span class="comment-number">#${index + 1}</span>
        <span class="comment-category category-${comment.category.toLowerCase()}">
          ${getCategoryIcon(comment.category)} ${comment.category}
        </span>
      </div>
      <div class="comment-text">${escapeHtml(comment.text)}</div>
    </div>
  `).join('');
}

function filterComments(filter) {
  console.log('🔍 Filtering comments by:', filter);
  console.log('📝 Available categories:', analyzedComments.map(c => c.category));
  currentFilter = filter;
  displayComments(analyzedComments);
}

function setActiveFilter(filter) {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.classList.remove('active');
  });
  document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
}

function updateCounts() {
  const counts = {
    all: analyzedComments.length,
    Good: analyzedComments.filter(c => c.category === 'Good').length,
    Neutral: analyzedComments.filter(c => c.category === 'Neutral').length,
    Bad: analyzedComments.filter(c => c.category === 'Bad').length
  };

  document.getElementById('allCount').textContent = counts.all;
  document.getElementById('goodCount').textContent = counts.Good;
  document.getElementById('neutralCount').textContent = counts.Neutral;
  document.getElementById('badCount').textContent = counts.Bad;
}

async function showSummary() {
  if (analyzedComments.length === 0) {
    showNotification('Please analyze comments first', 'warning');
    return;
  }

  const modal = document.getElementById('summaryModal');
  const loading = document.getElementById('summaryLoading');
  const content = document.getElementById('summaryContent');
  
  modal.style.display = 'flex';
  loading.style.display = 'block';
  content.style.display = 'none';

  try {
    const comments = analyzedComments.map(c => c.text);
    const summary = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: 'summarizeComments', comments },
        (response) => {
          if (response.error) {
            reject(new Error(response.error));
          } else {
            resolve(response.summary);
          }
        }
      );
    });

    loading.style.display = 'none';
    content.style.display = 'block';
    content.innerHTML = `<p>${escapeHtml(summary)}</p>`;

  } catch (error) {
    console.error('Error generating summary:', error);
    loading.style.display = 'none';
    content.style.display = 'block';
    content.innerHTML = `<p class="error">Error generating summary: ${escapeHtml(error.message)}</p>`;
  }
}

function closeSummary() {
  document.getElementById('summaryModal').style.display = 'none';
}

function updateStatus(message, type) {
  const statusText = document.querySelector('.status-text');
  const statusIndicator = document.querySelector('.status-indicator');
  
  statusText.textContent = message;
  statusIndicator.className = `status-indicator ${type}`;
}

function showLoadingOverlay(show) {
  document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

function showNotification(message, type) {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.innerHTML = `
    <span>${escapeHtml(message)}</span>
    <button onclick="this.parentElement.remove()">&times;</button>
  `;
  
  document.body.appendChild(notification);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

function getCategoryIcon(category) {
  switch (category) {
    case 'Good': return '😊';
    case 'Bad': return '😞';
    case 'Neutral': return '😐';
    default: return '📝';
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}