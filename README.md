# 🛡️ Social Guardian — Cyber Harassment Detector

> AI-powered Chrome extension that detects abusive comments on social media and generates formal FIR complaint PDFs in one click.

---

## 📸 What It Does

1. **Scans** comments on Instagram, Twitter/X, YouTube, and Facebook in real time
2. **Scores** each comment using an AI toxicity model (0–100%)
3. **Highlights** toxic comments red directly on the page
4. **Generates** a formal FIR (First Information Report) PDF complaint ready to submit to the police

---

## 🗂️ Project Structure

```
social-guardian-extension/      ← Load this folder in Chrome
├── manifest.json               ← Extension config (Manifest V3)
├── foreground.js               ← Scrapes & highlights comments on page
├── service-worker.js           ← Background service worker
├── service-worker-utils.js     ← Service worker helpers
├── popup/
│   ├── popup.html              ← Extension popup UI
│   ├── popup.css               ← Popup styles
│   └── popup.js                ← Dashboard + Profile + FIR logic
├── settings/
│   ├── settings.html           ← Settings page UI
│   └── settings.js             ← Settings save/load logic
└── logo/
    ├── logo-16.png
    ├── logo-48.png
    └── logo-128.png

backend/
├── app.py                      ← Flask API server
├── fir_generator.py            ← ReportLab PDF complaint generator
└── requirements.txt            ← Python dependencies
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Chrome Extension | Manifest V3, Vanilla JS |
| Toxicity Detection | [Detoxify](https://github.com/unitaryai/detoxify) (AI model) |
| Backend API | Python + Flask |
| PDF Generation | ReportLab |
| Storage | chrome.storage.local |

---

## 🚀 Setup & Installation

### Step 1 — Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

You should see:
```
Loading Detoxify model…
Model ready.
* Running on http://localhost:5000
```

> Keep this terminal open while using the extension.

### Step 2 — Chrome Extension

1. Open Chrome and go to `chrome://extensions`
2. Toggle **Developer Mode** ON (top right)
3. Click **Load Unpacked**
4. Select the `social-guardian-extension` folder
5. Click the 🧩 puzzle piece in Chrome toolbar → pin 📌 Social Guardian

---

## 🖥️ How to Use

### Fill Your Profile (first time)
1. Click the 🛡️ shield icon in your toolbar
2. Go to the **My Profile** tab
3. Enter your name, social handle, email, platform, and date of incident
4. Click **Save Profile**

### Scan for Harassment
1. Open Instagram, Twitter/X, YouTube, or Facebook
2. Click the shield icon → click **Scan Now**
3. Toxic comments get highlighted red on the page
4. Dashboard shows count of toxic and moderate comments

### Generate FIR PDF
1. After scanning, click **Generate FIR Complaint PDF**
2. PDF downloads automatically with all your details filled in
3. Submit to your local Cyber Crime Cell or police station

---

## 📊 Toxicity Score Scale

| Score | Level | Badge | Meaning |
|---|---|---|---|
| 85% – 100% | HIGH | 🔴 Red | Threatening / severe abuse |
| 60% – 84% | MEDIUM | 🟠 Orange | Moderate harassment |
| 0% – 59% | LOW | 🟢 Green | Likely safe |

---

## 📄 FIR PDF Contents

The generated complaint PDF includes:

- Complainant / victim details (from your Profile)
- Accused / offender username and platform
- Offensive comment (highlighted)
- AI toxicity score and category
- Incident description with relevant legal sections (IT Act, IPC)
- Supporting evidence checklist
- Formal prayer / request for investigation
- Signature block

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check if backend is running |
| `POST` | `/analyze` | Analyze comments for toxicity |
| `POST` | `/generate_fir` | Generate FIR PDF from evidence |

### Example `/analyze` request
```json
{
  "comments": ["You should die", "Great post!"],
  "platform": "Instagram",
  "victim_handle": "@bulbul_singh"
}
```

### Example `/analyze` response
```json
{
  "results": [
    {
      "comment": "You should die",
      "toxicity_score": 0.97,
      "is_toxic": true,
      "category": "Threat / Death Threat"
    }
  ]
}
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| Popup shows **offline** | Run `python app.py` in the backend folder |
| Extension won't load | Make sure `manifest.json` is at the root of the selected folder |
| `detoxify` install fails | Run `pip install detoxify --break-system-packages` |
| Port 5000 already in use | Change `app.run(port=5000)` to another port in `app.py` |
| Shield icon not visible | Click 🧩 puzzle piece in Chrome → pin Social Guardian |
| Comments not detected | Instagram/Twitter update their CSS selectors often — check `foreground.js` |

---

## 🏗️ System Architecture

```
Social Media Page
(Instagram / Twitter / YouTube / Facebook)
        ↓
Chrome Extension — foreground.js
(Scrapes comments from DOM)
        ↓
Flask Backend — app.py
(Receives comments via POST /analyze)
        ↓
Detoxify AI Model
(Scores each comment 0.0 – 1.0)
        ↓
Results stored in chrome.storage
        ↓
Popup Dashboard
(Shows toxic / moderate counts)
        ↓
Generate FIR — fir_generator.py
(ReportLab PDF complaint)
        ↓
Download PDF
(Ready to submit to Cyber Crime Cell)
```

---

## 📦 Dependencies

### Python (backend/requirements.txt)
```
flask
flask-cors
detoxify
reportlab
torch
transformers
```

### Chrome APIs used
- `chrome.storage.local` — stores scan results and profile
- `chrome.downloads` — triggers PDF download
- `chrome.scripting` — injects content scripts
- `chrome.tabs` — communicates with active tab

---

## ⚖️ Legal Sections Referenced in FIR

- **Section 66A** — Information Technology Act, 2000 (online harassment)
- **Section 507 IPC** — Criminal intimidation by anonymous communication
- **Section 354D IPC** — Stalking
- **Section 509 IPC** — Word, gesture or act intended to insult the modesty

---

## 🔒 Privacy

- All profile data is stored **locally** on your device using `chrome.storage.local`
- No data is sent to any external server except your local Flask backend (`localhost:5000`)
- The backend processes comments only during active scanning sessions

---

## 👩‍💻 Built With

- [SimGus/chrome-extension-v3-starter](https://github.com/SimGus/chrome-extension-v3-starter) — Extension boilerplate
- [Detoxify](https://github.com/unitaryai/detoxify) — Toxicity detection model
- [ReportLab](https://www.reportlab.com/) — PDF generation

---

*Built for hackathon — Cyber Safety Track*
