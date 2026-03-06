// service-worker.js — Social Guardian
// Replaces SimGus boilerplate service-worker.js

importScripts("service-worker-utils.js");

chrome.runtime.onInstalled.addListener(details => {
  if (details.reason === "install") {
    console.log("[Social Guardian] Installed successfully.");
  }
});

// Handle FIR PDF download requests from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "DOWNLOAD_FIR") {
    chrome.downloads.download(
      { url: message.url, filename: message.filename, saveAs: true },
      (id) => sendResponse({ ok: true, downloadId: id })
    );
    return true; // keep message channel open
  }
});
