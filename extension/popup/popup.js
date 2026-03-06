// popup.js — Social Guardian
// Full file: dashboard + profile tab + FIR generation

const BACKEND = "http://localhost:5000";

// ── Helpers ───────────────────────────────────────────────────────
function levelOf(score) {
  if (score >= 0.85) return "high";
  if (score >= 0.60) return "medium";
  return "low";
}
function labelOf(score) {
  if (score >= 0.85) return "HIGH";
  if (score >= 0.60) return "MED";
  return "LOW";
}
function animateNum(el, target) {
  const start = parseInt(el.textContent) || 0;
  if (start === target) return;
  const step = target > start ? 1 : -1;
  let cur = start;
  const t = setInterval(() => {
    cur += step;
    el.textContent = cur;
    if (cur === target) clearInterval(t);
  }, 30);
}

// ── Tab switching ─────────────────────────────────────────────────
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(p => p.style.display = "none");
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).style.display = "block";
  });
});

// ── Render scan results ───────────────────────────────────────────
function renderResults(results, platform) {
  const list   = document.getElementById("results-list");
  const total  = results.length;
  const toxic  = results.filter(r => r.toxicity_score >= 0.85).length;
  const medium = results.filter(r => r.toxicity_score >= 0.60 && r.toxicity_score < 0.85).length;

  animateNum(document.getElementById("stat-total"),  total);
  animateNum(document.getElementById("stat-toxic"),  toxic);
  animateNum(document.getElementById("stat-medium"), medium);

  if (platform) document.getElementById("platform-label").textContent = "📍 " + platform;
  if (toxic > 0) document.getElementById("fir-btn").disabled = false;

  if (total === 0) {
    list.innerHTML = `<div class="empty-state"><div class="empty-icon">✅</div><div class="empty-text">No harmful comments detected<br/>on this page.</div></div>`;
    return;
  }

  list.innerHTML = results.map(r => {
    const lvl  = levelOf(r.toxicity_score);
    const lbl  = labelOf(r.toxicity_score);
    const pct  = Math.round(r.toxicity_score * 100);
    const short = r.comment.length > 55 ? r.comment.slice(0, 52) + "…" : r.comment;
    const safe  = short.replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
    return `
      <div class="result-card ${lvl}">
        <div class="card-top">
          <div class="comment-preview" title="${safe}">"${safe}"</div>
          <span class="tox-badge ${lvl}">${lbl} ${pct}%</span>
        </div>
        <div class="card-meta">
          <span class="category-tag">${r.category || "Harassment"}</span>
          <div class="tox-bar-wrap"><div class="tox-bar-fill" style="width:${pct}%"></div></div>
        </div>
      </div>`;
  }).join("");
}

// ── Backend health check ──────────────────────────────────────────
async function checkBackend() {
  try {
    const res = await fetch(`${BACKEND}/health`, { signal: AbortSignal.timeout(2000) });
    const ok  = res.ok;
    document.getElementById("status-pill").className = "status-pill " + (ok ? "online" : "offline");
    document.getElementById("status-text").textContent = ok ? "online" : "offline";
    document.getElementById("offline-banner").classList.toggle("visible", !ok);
    return ok;
  } catch {
    document.getElementById("status-pill").className = "status-pill offline";
    document.getElementById("status-text").textContent = "offline";
    document.getElementById("offline-banner").classList.add("visible");
    return false;
  }
}

// ── Load stored scan results on popup open ────────────────────────
chrome.storage.local.get(
  ["sg_results", "sg_platform", "sg_scanned_at", "sg_offline"],
  (data) => {
    if (data.sg_scanned_at) {
      document.getElementById("scan-time").textContent = "last scan: " + data.sg_scanned_at;
    }
    if (data.sg_results && data.sg_results.length > 0) {
      renderResults(data.sg_results, data.sg_platform);
    }
    if (data.sg_offline) {
      document.getElementById("offline-banner").classList.add("visible");
    }
  }
);

checkBackend();

// ── Manual scan button ────────────────────────────────────────────
document.getElementById("scan-btn").addEventListener("click", () => {
  const btn = document.getElementById("scan-btn");
  btn.classList.add("spinning");
  btn.disabled = true;

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]) return;
    chrome.tabs.sendMessage(tabs[0].id, { action: "SCAN_NOW" }, () => {
      setTimeout(() => {
        chrome.storage.local.get(["sg_results","sg_platform","sg_scanned_at"], (data) => {
          if (data.sg_results) renderResults(data.sg_results, data.sg_platform);
          if (data.sg_scanned_at) {
            document.getElementById("scan-time").textContent = "last scan: " + data.sg_scanned_at;
          }
          btn.classList.remove("spinning");
          btn.disabled = false;
        });
      }, 2500);
    });
  });
});

// ── Generate FIR button ───────────────────────────────────────────
document.getElementById("fir-btn").addEventListener("click", async () => {
  const btn   = document.getElementById("fir-btn");
  const label = document.getElementById("fir-label");

  btn.disabled = true;
  btn.classList.add("loading");
  label.textContent = "Generating FIR…";

  // Load both scan results AND saved profile
  const data = await new Promise(res =>
    chrome.storage.local.get(["sg_results","sg_platform","sg_profile"], res)
  );

  const profile  = data.sg_profile || {};
  const topToxic = (data.sg_results || [])
    .filter(r => r.is_toxic || r.toxicity_score >= 0.60)
    .sort((a, b) => b.toxicity_score - a.toxicity_score)[0];

  if (!topToxic) {
    label.textContent = "No toxic content found";
    btn.classList.remove("loading");
    setTimeout(() => { label.textContent = "Generate FIR Complaint PDF"; btn.disabled = false; }, 2000);
    return;
  }

  // Format date from profile or today
  const incidentDate = profile.date
    ? new Date(profile.date).toLocaleDateString("en-IN", { day:"numeric", month:"long", year:"numeric" })
    : new Date().toLocaleDateString("en-IN", { day:"numeric", month:"long", year:"numeric" });

  try {
    const res = await fetch(`${BACKEND}/generate_fir`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        victim_handle:  "@" + (profile.handle  || "unknown"),
        victim_name:    profile.name            || "",
        victim_email:   profile.email           || "",
        victim_phone:   profile.phone           || "",
        victim_address: profile.address         || "",
        platform:       profile.platform || data.sg_platform || "Unknown",
        offender:       topToxic.offender       || "unknown_user",
        comment:        topToxic.comment,
        toxicity_score: topToxic.toxicity_score,
        category:       topToxic.category,
        date:           incidentDate,
      })
    });

    const blob     = await res.blob();
    const url      = URL.createObjectURL(blob);
    const filename = `FIR_${(profile.handle || "victim")}_${Date.now()}.pdf`;

    chrome.runtime.sendMessage({ action: "DOWNLOAD_FIR", url, filename });

    btn.classList.remove("loading");
    btn.classList.add("success");
    label.textContent = "✅ FIR Downloaded!";
    setTimeout(() => {
      btn.classList.remove("success");
      btn.disabled = false;
      label.textContent = "Generate FIR Complaint PDF";
    }, 3000);

  } catch (err) {
    btn.classList.remove("loading");
    btn.classList.add("error");
    label.textContent = "❌ Backend not running";
    setTimeout(() => {
      btn.classList.remove("error");
      btn.disabled = false;
      label.textContent = "Generate FIR Complaint PDF";
    }, 3000);
  }
});

// ── Settings link ─────────────────────────────────────────────────
document.getElementById("settings-link").addEventListener("click", () => {
  chrome.runtime.openOptionsPage();
});

// ══════════════════════════════════════════════════════════════════
//  PROFILE TAB
// ══════════════════════════════════════════════════════════════════

function loadProfile() {
  chrome.storage.local.get(["sg_profile"], (data) => {
    const p = data.sg_profile || {};
    if (p.name)     document.getElementById("p-name").value     = p.name;
    if (p.handle)   document.getElementById("p-handle").value   = p.handle;
    if (p.email)    document.getElementById("p-email").value    = p.email;
    if (p.phone)    document.getElementById("p-phone").value    = p.phone;
    if (p.address)  document.getElementById("p-address").value  = p.address;
    if (p.platform) document.getElementById("p-platform").value = p.platform;
    if (p.date)     document.getElementById("p-date").value     = p.date;

    // Show first letter of name as avatar
    if (p.name) {
      document.getElementById("avatar-display").textContent = p.name.trim()[0].toUpperCase();
    }

    // Show warning on dashboard if required fields are missing
    const complete = p.name && p.handle && p.email && p.platform;
    document.getElementById("profile-warn").classList.toggle("visible", !complete);
  });
}

loadProfile();

// Default date to today if not set
const dateInput = document.getElementById("p-date");
if (!dateInput.value) {
  dateInput.value = new Date().toISOString().split("T")[0];
}

// Save profile
document.getElementById("save-profile-btn").addEventListener("click", () => {
  const profile = {
    name:     document.getElementById("p-name").value.trim(),
    handle:   document.getElementById("p-handle").value.trim().replace(/^@/, ""),
    email:    document.getElementById("p-email").value.trim(),
    phone:    document.getElementById("p-phone").value.trim(),
    address:  document.getElementById("p-address").value.trim(),
    platform: document.getElementById("p-platform").value,
    date:     document.getElementById("p-date").value,
  };

  if (!profile.name || !profile.handle || !profile.email || !profile.platform) {
    const fb = document.getElementById("save-feedback");
    fb.style.color = "var(--red)";
    fb.textContent = "⚠ Fill required fields";
    setTimeout(() => fb.textContent = "", 2500);
    return;
  }

  chrome.storage.local.set({ sg_profile: profile }, () => {
    document.getElementById("avatar-display").textContent = profile.name[0].toUpperCase();
    document.getElementById("profile-warn").classList.remove("visible");
    const fb = document.getElementById("save-feedback");
    fb.style.color = "var(--green)";
    fb.textContent = "✓ Saved!";
    setTimeout(() => fb.textContent = "", 2000);
  });
});

// Clicking the warning banner jumps to Profile tab
document.getElementById("profile-warn").addEventListener("click", () => {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(p => p.style.display = "none");
  document.querySelector('[data-tab="profile"]').classList.add("active");
  document.getElementById("tab-profile").style.display = "block";
});
