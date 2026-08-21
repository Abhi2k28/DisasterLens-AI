import json
import re


DISASTER_KEYWORDS = [
    "flood",
    "flooding",
    "earthquake",
    "fire",
    "landslide",
    "cyclone",
    "storm",
    "tornado",
    "tsunami",
    "drought",
    "explosion"
]


def validate_report(report):
    if not report.get("text"):
        return False, "empty text"

    if not report.get("source"):
        return False, "missing source"

    if not report.get("timestamp"):
        return False, "missing timestamp"

    return True, "valid"


def clean_text(text):
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[!?]{2,}", "!", text)

    return text.strip()


def normalize_source(source):
    return source.strip().lower()


def is_duplicate(clean_text_value, seen_texts):
    if clean_text_value in seen_texts:
        return True

    seen_texts.add(clean_text_value)
    return False


def normalize_repeated_letters(text):
    return re.sub(r"(.)\1{2,}", r"\1", text)


def has_disaster_keyword(text):
    text_normalized = normalize_repeated_letters(text.lower())

    for keyword in DISASTER_KEYWORDS:
        if keyword in text_normalized:
            return True

    return False


# Input files
demo_file_path = "data/raw/demo_reports.json"
usgs_file_path = "data/raw/usgs_reports.json"

# Output files
output_path = "data/processed/processed_reports.json"
ai_output_path = "data/processed/ai_input.json"
quality_output_path = "data/processed/data_quality.json"


# Load demo reports
with open(demo_file_path, "r", encoding="utf-8") as file:
    demo_reports = json.load(file)


# Load USGS reports
with open(usgs_file_path, "r", encoding="utf-8") as file:
    usgs_reports = json.load(file)


# Combine reports
reports = demo_reports + usgs_reports


reports_received = len(reports)
valid_reports = 0
duplicates = 0
sent_to_ai = 0

seen_texts = set()
processed_reports = []
ai_input = []


for report in reports:

    valid, reason = validate_report(report)

    if not valid:
        print("Rejected:", reason)
        continue

    valid_reports += 1

    clean = clean_text(report["text"])
    normalized_source = normalize_source(report["source"])

    duplicate = is_duplicate(clean, seen_texts)

    if duplicate:
        duplicates += 1
        print("Duplicate skipped:", clean)
        continue

    keyword_match = has_disaster_keyword(clean)

    processed_report = {
        "source": normalized_source,
        "source_id": report.get("source_id"),
        "raw_text": report["text"],
        "clean_text": clean,
        "magnitude": report.get("magnitude"),
        "url": report.get("url"),
        "timestamp": report["timestamp"],
        "location": report.get("location"),
        "latitude": report.get("latitude"),
        "longitude": report.get("longitude"),
        "keyword_match": keyword_match
    }

    processed_reports.append(processed_report)

    if keyword_match:
        sent_to_ai += 1

        ai_report = {
            "text": clean,
            "source": normalized_source,
            "timestamp": report["timestamp"],
            "url": report.get("url"),
            "location": report.get("location"),
            "latitude": report.get("latitude"),
            "longitude": report.get("longitude"),
            "magnitude": report.get("magnitude")
        }

        ai_input.append(ai_report)


# Save processed reports
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(processed_reports, file, indent=2)


# Save AI input
with open(ai_output_path, "w", encoding="utf-8") as file:
    json.dump(ai_input, file, indent=2)


# Save data quality metrics
data_quality = {
    "reports_received": reports_received,
    "valid_reports": valid_reports,
    "duplicates": duplicates,
    "sent_to_ai": sent_to_ai,
    "processed_reports": len(processed_reports)
}


with open(quality_output_path, "w", encoding="utf-8") as file:
    json.dump(data_quality, file, indent=2)


# Pipeline metrics
print()
print("========== PIPELINE METRICS ==========")
print("Reports received:", reports_received)
print("Valid reports:", valid_reports)
print("Duplicates:", duplicates)
print("Sent to AI:", sent_to_ai)
print("Processed reports:", len(processed_reports))
print("AI input file:", ai_output_path)
print("=======================================")
print("Data quality report:", quality_output_path)