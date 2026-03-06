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
# 'original' is the base English model — fast and accurate
print("Loading Detoxify model...")
model = Detoxify('original')
print("Model loaded successfully!")

# ── Thresholds ───────────────────────────────────────────────
# A comment is flagged if ANY of these thresholds are crossed
TOXICITY_THRESHOLD = 0.6
INSULT_THRESHOLD   = 0.6
THREAT_THRESHOLD   = 0.5


# ── Root Endpoint ────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Social Guardian backend is running!"})


# ── Main Analysis Endpoint ───────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    # Step 1: Get JSON data sent from the Chrome extension
    data = request.get_json()

    # Step 2: Validate that 'comments' key exists and is a list
    if not data or "comments" not in data:
        return jsonify({"error": "Missing 'comments' in request body"}), 400

    comments = data["comments"]

    if not isinstance(comments, list) or len(comments) == 0:
        return jsonify({"error": "'comments' must be a non-empty list"}), 400

    # Step 3: Run Detoxify on all comments at once (batch = faster)
    results = model.predict(comments)
    # results is a dict like:
    # {
    #   "toxicity":    [0.88, 0.01],
    #   "insult":      [0.75, 0.02],
    #   "threat":      [0.12, 0.00],
    #   ...
    # }

    # Step 4: Build the response list
    response = []

    for i, comment in enumerate(comments):
        toxicity = round(float(results["toxicity"][i]), 4)
        insult   = round(float(results["insult"][i]),   4)
        threat   = round(float(results["threat"][i]),   4)

        # Step 5: Flag the comment if it crosses any threshold
        flagged = (
            toxicity > TOXICITY_THRESHOLD or
            insult   > INSULT_THRESHOLD   or
            threat   > THREAT_THRESHOLD
        )

        response.append({
            "comment":  comment,
            "toxicity": toxicity,
            "insult":   insult,
            "threat":   threat,
            "flagged":  flagged
        })

    return jsonify(response), 200


# ── Run Server ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)