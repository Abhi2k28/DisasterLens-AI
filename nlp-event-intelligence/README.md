# DisasterLens AI — NLP & Event Intelligence Module

This is the **NLP & Event Intelligence** part of DisasterLens AI (SIH hackathon).
It answers two questions only, per the team's division of responsibility:

- **NLP**: "What useful information is present in this report?"
- **Event Intelligence**: "Does this report belong to an existing real-world event?"

It does **not** decide whether something is a disaster (AI/ML's job), and does not
build the frontend, backend storage, or alerting.

No internet-dependent installs are required (no spaCy, no sentence-transformers
download) — everything runs on `scikit-learn`, which is already a standard
library, so this is safe to run on an unreliable connection.

---

## Files

| File | Purpose |
|---|---|
| `config.py` | Keyword lists, known-places gazetteer, matching threshold & weights |
| `models.py` | `Report` and `Event` data structures (shape agreed with backend) |
| `nlp_extractor.py` | Location extraction, impact/entity extraction, temporary disaster-type stub |
| `event_intelligence.py` | Similarity scoring, event matching, create/update logic, confidence & severity |
| `pipeline.py` | Wires NLP + Event Intelligence together for testing/demo |
| `demo.py` | Runs the exact example reports from the project spec, prints a jury-style trace |
| `test_pipeline.py` | Automated tests covering all 6 spec test cases + false positives |
| `api.py` | Flask HTTP wrapper so the backend can call this module over a REST endpoint |

---

## How to run

**1. Install dependencies** (only needed once; scikit-learn/Flask are common,
so this is usually a fast install even on a weak connection):

```
pip install scikit-learn flask
```

**2. Run the demo** (shows the full CREATE → UPDATE → dashboard flow):

```
python demo.py
```

**3. Run the automated tests:**

```
python test_pipeline.py
```
or, if you have pytest:
```
python -m pytest test_pipeline.py -v
```

**4. Run the API** (for backend integration):

```
python api.py
```
Then POST JSON to `http://localhost:5000/process-report`:
```json
{
  "text": "Heavy flooding has entered houses near Vijayawada.",
  "source": "reddit"
}
```

---

## How event matching works

```
NEW REPORT
    ↓
Compare against every ACTIVE event:
    - disaster type match   (hard gate)
    - time proximity        (hard gate: >12h apart = different event)
    - location match
    - semantic similarity (TF-IDF cosine)
    ↓
Weighted score → compared to threshold (0.60)
    ↓
Above threshold → UPDATE existing event
Below/no active events → CREATE new event
```

### Why two "hard gates" before the weighted score?

Short disaster sentences often share common words ("reported", the city name)
even when they describe *different* events. For example:

- `"Flooding reported in Vijayawada."`
- `"Fire reported in Vijayawada."`

These share 2 of 3 meaningful words, so text-similarity alone scores them
~0.7 similar — but the project spec is explicit that **FLOOD + FIRE should
probably be treated as different events**. So disaster type mismatch is
checked *first*, before any weighted math, and immediately blocks a match.

The same logic applies to time: if two reports are more than 12 hours apart,
they're treated as unrelated even if the text is identical, because a
report today shouldn't be silently merged into an old, possibly-resolved
event from a day and a half ago.

Only reports that pass **both gates** get scored by the weighted formula:

| Signal | Weight | Reasoning |
|---|---|---|
| Disaster type | 0.30 | Strong signal, but not the only one (see gate above) |
| Location | 0.30 | Same city is one of the strongest "same event" signals |
| Time proximity | 0.15 | Useful, but reports about the same event can be minutes apart |
| Semantic similarity | 0.25 | Catches reworded/paraphrased reports about the same thing |

### Threshold reasoning (0.60)

Tested against the spec's own examples:

- Reports genuinely about the **same** event (same type/location, close in
  time, reworded text) scored **0.70–0.90** in testing.
- Reports about **different** events that pass the gates (e.g. same city,
  same type, but describing something new) tend to fall below that.
- **0.60** sits below the "same event" cluster with margin, while still
  being high enough that a single vague, low-signal report doesn't
  auto-merge into an unrelated event.

This is an **MVP threshold**, tuned by hand against the spec's test cases —
not statistically validated. If your demo data behaves differently, adjust
`MATCH_THRESHOLD` in `config.py` and re-run `test_pipeline.py`.

---

## Confidence score — what it does and doesn't mean

`event_confidence` combines:
- the (stubbed) AI/ML confidence that the report is a real disaster,
- how well the report matched the event it joined,
- a small bonus for multiple independent sources agreeing,
- a small bonus for more accumulated reports.

**This is an explainable MVP heuristic, not a scientifically validated
probability.** Say so if a judge asks.

---

## Known limitations (be upfront about these in the demo)

- **Disaster type classification is currently a keyword-based stub**
  (`nlp_extractor.classify_disaster_type_stub`) standing in for the AI/ML
  teammate's real classifier. Swap it out — the rest of the pipeline
  doesn't need to change, as long as the replacement returns
  `(is_disaster: bool, disaster_type: str|None, confidence: float)`.
- **Location extraction** uses a small hand-written gazetteer + regex
  patterns (`in/near/at/from <Place>`), not a trained NER model. It will
  miss locations not written in that pattern, and won't recognize places
  outside the gazetteer unless they happen to follow that pattern.
- **Semantic similarity** uses TF-IDF word-overlap, not deep embeddings —
  it catches reworded sentences that share vocabulary, but won't catch two
  completely different phrasings of the same idea (e.g. no shared words at
  all). If you get internet access later, swapping in
  `sentence-transformers` (e.g. `all-MiniLM-L6-v2`) is a drop-in upgrade to
  `_semantic_similarity()` in `event_intelligence.py`.
- **No persistence** — `EventStore` is in-memory. The real backend owns
  storage; this is only for independent development/testing.

---

## Handoff contract for the backend

Call `pipeline.process_raw_report(text, timestamp, source, store)` or the
`/process-report` HTTP endpoint. You'll get back:

```json
{
  "action": "CREATE",
  "event_id": "EVENT-002",
  "event_confidence": 0.89,
  "match_breakdown": { "type_score": 1.0, "location_score": 1.0, "time_score": 0.95, "semantic_score": 0.4, "final_score": 0.72 },
  "event": {
    "event_id": "EVENT-002",
    "disaster_type": "FLOOD",
    "location": "Visakhapatnam",
    "latitude": null,
    "longitude": null,
    "first_report_time": "2026-08-20T10:35:00",
    "last_report_time": "2026-08-20T10:35:00",
    "report_count": 1,
    "severity": "LOW",
    "event_confidence": 0.89,
    "status": "ACTIVE"
  }
}
```

Confirm field names with the backend dev before they build storage around
this — per the spec, don't assume the contract.
