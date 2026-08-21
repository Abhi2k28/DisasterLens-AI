# DisasterLens AI — AI/ML Component

Beginner-friendly zero-shot disaster detection & classification, built for
the SIH Internal Hackathon. This is the **AI/ML Engineer's** part only
(see project architecture below) — not frontend, database, alerts, event
clustering, or data collection.

---

## 1. What this does

Given a raw text report (e.g. from social media or news), this component:

1. Cleans the text (`preprocessing/cleaner.py`)
2. Decides if it's a **real disaster report** vs unrelated/movie/joke text
3. If it is, classifies the **disaster type** (flood, fire, earthquake, etc.)
4. Returns an **AI confidence score** (not a guaranteed real-world probability)
5. Estimates **severity** (LOW / MEDIUM / HIGH) using simple keyword signals
6. Outputs structured JSON ready to hand off to the NLP/Event Intelligence
   teammate

Model used: `facebook/bart-large-mnli` via Hugging Face's zero-shot
classification pipeline. No training required — it's used as-is.

---

## 2. Setup (do this first, in order)

**Step A — Check Python** (need 3.9–3.11 ideally)

COMMAND PROMPT:
```
python --version
```

**Step B — Create and activate a virtual environment** (recommended, keeps
dependencies clean)

COMMAND PROMPT:
```
python -m venv venv
venv\Scripts\activate
```

**Step C — Install dependencies**

COMMAND PROMPT:
```
pip install -r requirements.txt
```

This installs PyTorch, Transformers, scikit-learn, pandas, numpy. This step
needs internet and may take a few minutes.

**Step D — First model run (downloads the model, ~1.6 GB)**

COMMAND PROMPT:
```
python model/classifier.py
```

- This needs internet the **first** time only. After that, the model is
  cached locally (usually under `C:\Users\<you>\.cache\huggingface`) and
  won't be re-downloaded.
- Expect this first run to take a while depending on your connection —
  that's normal, it's a large model.
- You should see two printed dicts at the end, one for the flood example
  (should show `is_disaster: True`, type `FLOOD`) and one for the movie
  example (should show `is_disaster: False`).

**Step E — Run the full pipeline demo**

COMMAND PROMPT:
```
python api/inference.py
```

This runs 4 sample reports end-to-end and prints structured JSON for each.

**Step F — Run the test suite**

COMMAND PROMPT:
```
python tests/test_classifier.py
```

This runs the exact test reports from the spec (real disaster tests +
false-positive tests) and tells you where results matched expectations and
where you should manually review.

---

## 3. Project structure

```
disasterlens-ai/
│
├── model/
│   └── classifier.py        # loads model once, does the actual classification
│
├── preprocessing/
│   └── cleaner.py            # cleans raw text (URLs, mentions, hashtags, etc.)
│
├── tests/
│   └── test_classifier.py    # runs spec's test reports + false-positive tests
│
├── api/
│   └── inference.py          # ties it together, loads model once, adds
│                              # timestamp/location, exposes analyze_report()
│
├── requirements.txt
└── README.md
```

---

## 4. How your teammates plug into this

**NLP / Event Intelligence teammate:**
```python
from api.inference import analyze_report

result = analyze_report("Heavy flooding reported near Vijayawada.", location="Vijayawada")
# result = {
#   "is_disaster": True,
#   "disaster_type": "FLOOD",
#   "confidence": 0.91,
#   "severity": "HIGH",
#   "text": "Heavy flooding reported near Vijayawada.",
#   "timestamp": "2026-08-20T10:30:00+00:00",
#   "location": "Vijayawada"
# }
```

**Backend developer:** a commented-out minimal Flask example is included at
the bottom of `api/inference.py` (`POST /api/analyze`) in case you need
something runnable fast. **Don't assume this is the real contract** — confirm
the actual API shape with your backend developer.

---

## 5. Important limitations (say this out loud in your demo)

- The AI model detects **signals in text**. It does **not** physically detect
  a disaster.
- It does **not guarantee** a disaster is occurring — it flags *probable*
  disaster-related reports with a confidence score.
- "Confidence" means **AI model confidence**, not a real-world probability.
- Severity is a simple, explainable **MVP estimate** based on keyword
  signals — not an official emergency assessment.
- The system provides **early intelligence** from available reports; it does
  not replace official authorities.

---

## 6. If accuracy isn't great during testing

Zero-shot models are decent but not perfect out of the box, especially on
the "is this really a disaster" (relevance) step — that's the hardest part.
If `tests/test_classifier.py` shows misclassifications:

1. Try rewording the two `RELEVANCE_LABELS` sentences in
   `model/classifier.py` — small wording changes can noticeably change
   zero-shot results.
2. Re-run `tests/test_classifier.py` and compare.
3. Don't train a new model during the hackathon (per spec) — tune the
   labels/thresholds instead, and be upfront in the demo about the model's
   known limitations.

## 7. Performance note

CPU inference on a normal laptop will be noticeably slower than GPU (maybe
1–3 seconds per report) — this is expected and fine for an MVP demo. Don't
spend hackathon time chasing GPU optimization (per spec, Rule 17).
