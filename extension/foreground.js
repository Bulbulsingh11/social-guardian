// foreground.js — Social Guardian
// Replaces SimGus boilerplate foreground.js
// Scrapes comments, sends to Flask backend, highlights toxic content in-page.

const BACKEND = "http://localhost:5000/analyze";

const PLATFORM_SELECTORS = {
  "instagram.com": "span.x193iq5w, span._aacl",
  "twitter.com":   "div[data-testid='tweetText']",
  "x.com":         "div[data-testid='tweetText']",
  "youtube.com":   "yt-formatted-string#content-text",
  "facebook.com":  "div[data-ad-comet-preview='message']"
};

function getPlatform() {
  const host = window.location.hostname;
  for (const key of Object.keys(PLATFORM_SELECTORS)) {
    if (host.includes(key)) return key;
  }
  return null;
}

function scrapeComments() {
  const platform = getPlatform();
  if (!platform) return [];
  const selector = PLATFORM_SELECTORS[platform];
  return Array.from(document.querySelectorAll(selector))
    .map(el => el.innerText.trim())
    .filter(t => t.length > 2)
    .slice(0, 30);
}

function getVictimHandle() {
  const og = document.querySelector("meta[property='og:title']");
  if (og && og.content) return "@" + og.content.split(/[\s|·]/)[0].replace(/^@/, "");
  const path = window.location.pathname.split("/").filter(Boolean)[0];
  return path ? "@" + path : "@unknown";
}

async function analyzeAndStore() {
  const comments = scrapeComments();
  if (!comments.length) return;

  try {
    const res = await fetch(BACKEND, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        comments,
        platform:      getPlatform(),
        victim_handle: getVictimHandle(),
        page_url:      window.location.href
      })
    });
    const data = await res.json();

    chrome.storage.local.set({
      sg_results:       data.results,
      sg_platform:      getPlatform(),
      sg_victim:        getVictimHandle(),
      sg_scanned_at:    new Date().toLocaleTimeString(),
      sg_total:         data.results.length,
      sg_toxic_count:   data.results.filter(r => r.toxicity_score >= 0.85).length,
      sg_medium_count:  data.results.filter(r => r.toxicity_score >= 0.60 && r.toxicity_score < 0.85).length,
    });

    paintToxicComments(data.results);
  } catch (e) {
    // backend offline — store empty sentinel
    chrome.storage.local.set({ sg_offline: true });
  }
}

function paintToxicComments(results) {
  const platform = getPlatform();
  if (!platform) return;
  const nodes = document.querySelectorAll(PLATFORM_SELECTORS[platform]);

  nodes.forEach(el => {
    const text  = el.innerText.trim();
    const match = results.find(r => r.comment === text);
    if (!match || match.toxicity_score < 0.60) return;

    const isHigh = match.toxicity_score >= 0.85;
    el.style.cssText = `
      background: ${isHigh ? "#fff0f0" : "#fff8ee"} !important;
      border-left: 3px solid ${isHigh ? "#e74c3c" : "#e67e22"} !important;
      padding: 3px 8px !important;
      border-radius: 4px !important;
      transition: background 0.3s !important;
    `;
    el.title = `🛡️ Social Guardian: ${Math.round(match.toxicity_score * 100)}% toxic — ${match.category}`;
  });
}

// Initial scan + periodic rescan for dynamic pages
analyzeAndStore();
setInterval(analyzeAndStore, 10000);

// Listen for manual scan trigger from popup
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "SCAN_NOW") {
    analyzeAndStore().then(() => sendResponse({ ok: true }));
    return true;
  }
});
