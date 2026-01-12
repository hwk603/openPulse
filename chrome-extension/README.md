# OpenPulse Chrome Extension

A Chrome browser extension for real-time GitHub repository health monitoring.

## Features

- 🔮 **Real-time Health Scores**: View repository health scores directly on GitHub
- 📊 **Six-Dimensional Analysis**: Activity, Diversity, Response Time, Code Quality, Documentation, Community
- ⚠️ **Smart Alerts**: Color-coded warnings based on repository health
- 🎯 **Lifecycle Detection**: Identify repository stage (Embryonic, Growth, Mature, Decline)
- 💡 **Instant Insights**: One-click analysis from any GitHub repository page

## Installation

### Development Mode

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the `chrome-extension` directory from this project
5. The OpenPulse extension icon should appear in your toolbar

### Prerequisites

- OpenPulse API must be running on `http://localhost:8000`
- Start the API with: `python -m uvicorn src.api.main:app --reload`

## Usage

### Method 1: Extension Popup

1. Navigate to any GitHub repository page
2. Click the OpenPulse extension icon in your toolbar
3. View comprehensive health metrics and analysis

### Method 2: In-Page Widget

1. Navigate to any GitHub repository page
2. A floating health widget will appear in the bottom-right corner
3. View quick health score and lifecycle stage

## Features Explained

### Health Score (0-100)

- **90-100**: Excellent - Thriving community
- **75-89**: Good - Healthy and stable
- **60-74**: Fair - Room for improvement
- **40-59**: Poor - Needs attention
- **0-39**: Critical - Immediate action required

### Alert Levels

- 🟢 **Green**: Healthy repository
- 🟡 **Yellow**: Minor concerns
- 🟠 **Orange**: Moderate issues
- 🔴 **Red**: Critical problems

### Lifecycle Stages

- **Embryonic**: New project, small community
- **Growth**: Rapidly expanding
- **Mature**: Stable and established
- **Decline**: Decreasing activity
- **Revival**: Recovering from decline

## Configuration

Edit `popup.js` to change the API endpoint:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

## Permissions

The extension requires:

- `activeTab`: To read the current GitHub repository URL
- `storage`: To cache analysis results
- `https://github.com/*`: To inject health widgets
- `http://localhost:8000/*`: To communicate with the API

## Development

### File Structure

```
chrome-extension/
├── manifest.json       # Extension configuration
├── popup.html         # Extension popup UI
├── popup.js           # Popup logic
├── content.js         # Content script (injected into GitHub)
├── content.css        # Content script styles
├── background.js      # Background service worker
└── icons/            # Extension icons
```

### Testing

1. Make changes to the extension files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the OpenPulse extension card
4. Test on a GitHub repository page

## Troubleshooting

### "Failed to analyze repository"

- Ensure the OpenPulse API is running on `http://localhost:8000`
- Check browser console for detailed error messages
- Verify the repository has been added to OpenPulse monitoring

### Widget not appearing

- Refresh the GitHub page
- Check that you're on a repository main page (not issues, PRs, etc.)
- Verify the extension is enabled in `chrome://extensions/`

### CORS errors

- The API must allow requests from `chrome-extension://` origins
- Check API CORS configuration in `src/api/main.py`

## Future Enhancements

- [ ] Contributor churn predictions in popup
- [ ] Historical health trends chart
- [ ] Comparison with similar repositories
- [ ] Export health reports
- [ ] Notifications for health changes
- [ ] Support for GitLab and Gitee

## License

Apache 2.0 - See LICENSE file for details
