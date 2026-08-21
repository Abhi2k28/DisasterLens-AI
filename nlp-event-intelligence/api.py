"""
api.py
------
Minimal Flask wrapper so the backend developer can call your module
over HTTP instead of importing Python directly. This is a STARTING
POINT -- confirm the actual request/response contract with your
backend teammate and adjust field names if needed (per spec:
"Do NOT assume the actual API endpoint. Ask the backend developer.")

Run with:   python api.py
Then POST to http://localhost:5000/process-report

Example request body:
{
    "text": "Heavy flooding has entered houses near Vijayawada.",
    "timestamp": "2026-08-20T10:30:00",
    "source": "reddit"
}

Example response body:
{
    "action": "CREATE",
    "event_id": "EVENT-001",
    "event_confidence": 0.92,
    "match_breakdown": {...},
    "event": {...}
}
"""

from datetime import datetime
from flask import Flask, request, jsonify

from pipeline import process_raw_report
from event_intelligence import EventStore

app = Flask(__name__)

# One shared in-memory store for the life of this process.
# The backend will eventually own real persistence -- this is only
# so the endpoint is demoable standalone.
store = EventStore()


@app.route("/process-report", methods=["POST"])
def process_report_endpoint():
    data = request.get_json(force=True, silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Request body must include 'text'"}), 400

    text = data["text"]
    source = data.get("source", "unknown")

    ts_raw = data.get("timestamp")
    timestamp = datetime.fromisoformat(ts_raw) if ts_raw else datetime.utcnow()

    result = process_raw_report(text, timestamp, source, store)
    return jsonify(result)


@app.route("/events", methods=["GET"])
def list_events():
    """Convenience endpoint so frontend/backend can sanity-check state
    while wiring things up -- not necessarily the final contract."""
    return jsonify([e.to_dict() for e in store.events.values()])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
