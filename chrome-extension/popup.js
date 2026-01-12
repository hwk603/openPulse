// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Get current repository info from active tab
async function getCurrentRepo() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const url = tab.url;

  // Parse GitHub URL
  const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/);
  if (!match) {
    throw new Error('Not a GitHub repository page');
  }

  return {
    platform: 'github',
    owner: match[1],
    repo: match[2].replace(/\?.*$/, '').replace(/#.*$/, ''),
    url: url
  };
}

// Fetch health assessment from API
async function fetchHealthAssessment(owner, repo) {
  const response = await fetch(`${API_BASE_URL}/health-assessment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      platform: 'github',
      owner: owner,
      repo: repo
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

// Update UI with health data
function updateUI(repoInfo, healthData) {
  // Update repo info
  document.getElementById('repoName').textContent = `${repoInfo.owner}/${repoInfo.repo}`;
  document.getElementById('repoUrl').textContent = repoInfo.url;

  // Update health score
  const score = Math.round(healthData.overall_score);
  document.getElementById('scoreValue').textContent = score;

  // Update score circle gradient
  const scoreDeg = (score / 100) * 360;
  document.getElementById('scoreCircle').style.setProperty('--score-deg', `${scoreDeg}deg`);

  // Update lifecycle badge
  document.getElementById('lifecycleBadge').textContent = healthData.lifecycle_stage.toUpperCase();

  // Update metrics
  document.getElementById('activityScore').textContent = Math.round(healthData.activity_score);
  document.getElementById('diversityScore').textContent = Math.round(healthData.diversity_score);
  document.getElementById('responseScore').textContent = Math.round(healthData.response_time_score);
  document.getElementById('communityScore').textContent = Math.round(healthData.community_atmosphere_score);

  // Generate alerts
  const alertsContainer = document.getElementById('alerts');
  alertsContainer.innerHTML = '';

  // Determine alert level based on score
  let alertLevel = 'green';
  let alertTitle = 'Healthy Repository';
  let alertMessage = 'This repository shows good health indicators.';

  if (score < 40) {
    alertLevel = 'red';
    alertTitle = 'Critical Health Issues';
    alertMessage = 'This repository needs immediate attention. Consider reviewing contributor engagement and activity levels.';
  } else if (score < 60) {
    alertLevel = 'orange';
    alertTitle = 'Health Concerns';
    alertMessage = 'Some health metrics are below optimal levels. Monitor contributor activity closely.';
  } else if (score < 75) {
    alertLevel = 'yellow';
    alertTitle = 'Room for Improvement';
    alertMessage = 'Repository is stable but could benefit from increased community engagement.';
  }

  const alert = document.createElement('div');
  alert.className = `alert ${alertLevel}`;
  alert.innerHTML = `
    <div class="alert-title">${alertTitle}</div>
    <div class="alert-message">${alertMessage}</div>
  `;
  alertsContainer.appendChild(alert);
}

// Show error
function showError(message) {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('content').style.display = 'none';
  document.getElementById('error').style.display = 'block';
  document.getElementById('errorMessage').textContent = message;
}

// Main function
async function analyzeRepository() {
  try {
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display = 'none';
    document.getElementById('error').style.display = 'none';

    // Get current repo
    const repoInfo = await getCurrentRepo();

    // Fetch health assessment
    const healthData = await fetchHealthAssessment(repoInfo.owner, repoInfo.repo);

    // Update UI
    updateUI(repoInfo, healthData);

    // Show content
    document.getElementById('loading').style.display = 'none';
    document.getElementById('content').style.display = 'block';

  } catch (error) {
    console.error('Error:', error);
    showError(error.message || 'Failed to analyze repository. Make sure the OpenPulse API is running.');
  }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  analyzeRepository();

  document.getElementById('refreshBtn').addEventListener('click', () => {
    analyzeRepository();
  });
});
