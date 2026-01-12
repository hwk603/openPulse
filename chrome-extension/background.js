// Background service worker

chrome.runtime.onInstalled.addListener(() => {
  console.log('OpenPulse extension installed');
});

// Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeRepo') {
    // Handle repository analysis request
    console.log('Analyzing repository:', request.repo);
    sendResponse({ status: 'success' });
  }
  return true;
});
