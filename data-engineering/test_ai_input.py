import json


FILE_PATH = "data/processed/ai_input.json"


with open(FILE_PATH, "r", encoding="utf-8") as file:
    reports = json.load(file)


print("AI reports found:", len(reports))


required_fields = [
    "text",
    "source",
    "timestamp",
    "url"
]


validation_passed = True


for report in reports:
    for field in required_fields:
        if field not in report:
            print("Missing field:", field)
            validation_passed = False


usgs_reports = [
    report for report in reports
    if report.get("source") == "usgs"
]


print("USGS reports found:", len(usgs_reports))


if len(usgs_reports) == 0:
    print("USGS validation: FAILED")
    validation_passed = False
else:
    print("USGS validation: PASSED")


if validation_passed:
    print("AI input validation: PASSED")
else:
    print("AI input validation: FAILED")