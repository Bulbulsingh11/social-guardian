# ============================================================
#  Social Guardian - Backend API
#  Flask + Detoxify toxicity detection
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
from detoxify import Detoxify

# ── App Setup ────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow Chrome extension to send requests (cross-origin)

# ── Load Detoxify Model ──────────────────────────────────────
# Loading once at startup so it doesn't reload on every request
print("Loading Detoxify model...")
model = Detoxify('original')
print("Model loaded successfully!")

# ── Thresholds ───────────────────────────────────────────────
TOXICITY_THRESHOLD = 0.60
INSULT_THRESHOLD   = 0.60
THREAT_THRESHOLD   = 0.50


# ── Helper: pick dominant category label ─────────────────────
def get_category(toxicity, insult, threat, severe, obscene, identity):
    scores = {
        "Threat / Death Threat":       threat,
        "Insult / Personal Attack":    insult,
        "Severe Toxicity":             severe,
        "Obscene Language":            obscene,
        "Identity-Based Harassment":   identity,
        "General Toxicity":            toxicity,
    }
    return max(scores, key=scores.get)


# ── Root Endpoint ────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Social Guardian backend is running!"})


# ── Health Check (used by popup to show online/offline) ──────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "detoxify-original"})


# ── Main Analysis Endpoint ───────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    # Step 1: Get JSON data sent from the Chrome extension
    data = request.get_json()

    # Step 2: Validate input
    if not data or "comments" not in data:
        return jsonify({"error": "Missing 'comments' in request body"}), 400

    comments = data["comments"]

    if not isinstance(comments, list) or len(comments) == 0:
        return jsonify({"error": "'comments' must be a non-empty list"}), 400

    platform      = data.get("platform",      "Unknown")
    victim_handle = data.get("victim_handle", "unknown")

    # Step 3: Run Detoxify on all comments at once (batch = faster)
    raw = model.predict(comments)
    # raw is a dict like:
    # {
    #   "toxicity":        [0.88, 0.01],
    #   "insult":          [0.75, 0.02],
    #   "threat":          [0.12, 0.00],
    #   "severe_toxicity": [...],
    #   "obscene":         [...],
    #   "identity_attack": [...],
    # }

    # Step 4: Build the response list
    results = []

    for i, comment in enumerate(comments):
        toxicity = round(float(raw["toxicity"][i]),        4)
        insult   = round(float(raw["insult"][i]),          4)
        threat   = round(float(raw["threat"][i]),          4)
        severe   = round(float(raw["severe_toxicity"][i]), 4)
        obscene  = round(float(raw["obscene"][i]),         4)
        identity = round(float(raw["identity_attack"][i]), 4)

        # Flag if any threshold crossed
        is_toxic = (
            toxicity > TOXICITY_THRESHOLD or
            insult   > INSULT_THRESHOLD   or
            threat   > THREAT_THRESHOLD
        )

        results.append({
            "comment":        comment,
            "toxicity_score": toxicity,   # used by popup.js for badge + bar
            "is_toxic":       is_toxic,   # used by popup.js to enable FIR button
            "category":       get_category(toxicity, insult, threat, severe, obscene, identity),
            "offender":       "unknown_user",  # extension can enrich this later
            "all_scores": {
                "toxicity":        toxicity,
                "insult":          insult,
                "threat":          threat,
                "severe_toxicity": severe,
                "obscene":         obscene,
                "identity_attack": identity,
            }
        })

    # Sort: most toxic first
    results.sort(key=lambda x: x["toxicity_score"], reverse=True)

    return jsonify({
        "results":        results,
        "platform":       platform,
        "victim_handle":  victim_handle,
        "total":          len(results),
        "toxic_count":    sum(1 for r in results if r["is_toxic"]),
    }), 200


# ── FIR Generation Endpoint ──────────────────────────────────
@app.route("/generate_fir", methods=["POST"])
def generate_fir_endpoint():
    import tempfile, os
    from datetime import datetime
    from flask import send_file
    from fir_generator import generate_fir

    data = request.get_json()

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()

    generate_fir(data, output_path=tmp.name)

    victim   = data.get("victim_handle", "victim").lstrip("@")
    filename = f"FIR_{victim}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return send_file(
        tmp.name,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


# ── Run Server ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)