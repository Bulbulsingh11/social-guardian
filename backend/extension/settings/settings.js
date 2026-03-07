// settings.js
const keys = ["backend-url","tox-threshold","mod-threshold","auto-scan","highlight"];

// Load saved settings
chrome.storage.local.get(["sg_settings"], (data) => {
  const s = data.sg_settings || {};
  if (s.backendUrl)     document.getElementById("backend-url").value    = s.backendUrl;
  if (s.toxThreshold)   document.getElementById("tox-threshold").value  = s.toxThreshold;
  if (s.modThreshold)   document.getElementById("mod-threshold").value  = s.modThreshold;
  if (s.autoScan  !== undefined) document.getElementById("auto-scan").checked  = s.autoScan;
  if (s.highlight !== undefined) document.getElementById("highlight").checked  = s.highlight;
  updateLabels();
});

function updateLabels() {
  document.getElementById("tox-val").textContent = document.getElementById("tox-threshold").value;
  document.getElementById("mod-val").textContent = document.getElementById("mod-threshold").value;
}

document.getElementById("tox-threshold").addEventListener("input", updateLabels);
document.getElementById("mod-threshold").addEventListener("input", updateLabels);

document.getElementById("save-btn").addEventListener("click", () => {
  const settings = {
    backendUrl:    document.getElementById("backend-url").value || "http://localhost:5000",
    toxThreshold:  parseFloat(document.getElementById("tox-threshold").value),
    modThreshold:  parseFloat(document.getElementById("mod-threshold").value),
    autoScan:      document.getElementById("auto-scan").checked,
    highlight:     document.getElementById("highlight").checked,
  };
  chrome.storage.local.set({ sg_settings: settings }, () => {
    const msg = document.getElementById("saved-msg");
    msg.classList.add("show");
    setTimeout(() => msg.classList.remove("show"), 2000);
  });
});
