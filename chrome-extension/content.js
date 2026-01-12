// Content script - Injects health indicator into GitHub repository page

// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create health indicator widget
function createHealthWidget() {
  const widget = document.createElement('div');
  widget.id = 'openpulse-widget';
  widget.innerHTML = `
    <div class="openpulse-container">
      <div class="openpulse-header">
        <span class="openpulse-icon">🔮</span>
        <span class="openpulse-title">OpenPulse Health</span>
      </div>
      <div class="openpulse-content">
        <div class="openpulse-score" id="openpulse-score">
          <div class="score-value">--</div>
          <div class="score-label">Health Score</div>
        </div>
        <div class="openpulse-badge" id="openpulse-badge">Analyzing...</div>
      </div>
    </div>
  `;
  return widget;
}

// Extract repository info from current page
function getRepoInfo() {
  const pathParts = window.location.pathname.split('/').filter(p => p);
  if (pathParts.length >= 2) {
    return {
      owner: pathParts[0],
      repo: pathParts[1]
    };
  }
  return null;
}

// Fetch and display health score
async function fetchAndDisplayHealth() {
  const repoInfo = getRepoInfo();
  if (!repoInfo) return;

  try {
    const response = await fetch(`${API_BASE_URL}/health-assessment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        platform: 'github',
        owner: repoInfo.owner,
        repo: repoInfo.repo
      })
    });

    if (response.ok) {
      const data = await response.json();
      updateWidget(data);
    }
  } catch (error) {
    console.error('OpenPulse: Failed to fetch health data', error);
  }
}

// Update widget with health data
function updateWidget(healthData) {
  const scoreElement = document.querySelector('#openpulse-score .score-value');
  const badgeElement = document.getElementById('openpulse-badge');

  if (scoreElement && badgeElement) {
    const score = Math.round(healthData.overall_score);
    scoreElement.textContent = score;

    // Update badge color based on score
    let badgeClass = 'badge-green';
    if (score < 40) badgeClass = 'badge-red';
    else if (score < 60) badgeClass = 'badge-orange';
    else if (score < 75) badgeClass = 'badge-yellow';

    badgeElement.className = `openpulse-badge ${badgeClass}`;
    badgeElement.textContent = healthData.lifecycle_stage.toUpperCase();
  }
}

// Initialize
function init() {
  // Check if we're on a repository page
  if (!window.location.pathname.match(/^\/[^\/]+\/[^\/]+\/?$/)) {
    return;
  }

  // Find the repository header
  const repoHeader = document.querySelector('.pagehead') || document.querySelector('[data-pjax-container]');

  if (repoHeader) {
    const widget = createHealthWidget();
    repoHeader.appendChild(widget);

    // Fetch health data
    fetchAndDisplayHealth();
  }
}

// Run on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
