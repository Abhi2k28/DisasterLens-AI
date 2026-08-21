"""
test_pipeline.py
-----------------
Automated versions of the TEST CASES section from the project spec.

Run with:   python -m pytest test_pipeline.py -v
       or:  python test_pipeline.py   (runs without pytest too)
"""

from datetime import datetime, timedelta
from pipeline import process_raw_report
from event_intelligence import EventStore


def test_case_1_create_event():
    store = EventStore()
    r = process_raw_report("Flooding reported in Vijayawada.", datetime(2026, 8, 20, 10, 30), "demo", store)
    assert r["action"] == "CREATE"


def test_case_2_update_event():
    store = EventStore()
    process_raw_report("Flooding reported in Vijayawada.", datetime(2026, 8, 20, 10, 30), "demo", store)
    r2 = process_raw_report("Flooding reported in Vijayawada again.", datetime(2026, 8, 20, 10, 35), "demo", store)
    assert r2["action"] == "UPDATE"


def test_case_3_new_location_new_event():
    store = EventStore()
    process_raw_report("Flooding reported in Vijayawada.", datetime(2026, 8, 20, 10, 30), "demo", store)
    r2 = process_raw_report("Flooding reported in Visakhapatnam.", datetime(2026, 8, 20, 10, 35), "demo", store)
    assert r2["action"] == "CREATE"


def test_case_4_new_type_new_event():
    store = EventStore()
    process_raw_report("Flooding reported in Vijayawada.", datetime(2026, 8, 20, 10, 30), "demo", store)
    r2 = process_raw_report("Fire reported in Vijayawada.", datetime(2026, 8, 20, 10, 40), "demo", store)
    assert r2["action"] == "CREATE"


def test_case_5_similar_text_same_event():
    store = EventStore()
    process_raw_report("Heavy flooding has entered houses near Vijayawada.", datetime(2026, 8, 20, 10, 30), "demo", store)
    r2 = process_raw_report("Water entered several homes in Vijayawada due to heavy rain.",
                             datetime(2026, 8, 20, 10, 33), "demo", store)
    assert r2["action"] == "UPDATE"


def test_case_6_far_apart_time_new_event():
    """Same text, but far enough apart in time (>TIME_WINDOW_HOURS) that
    it should NOT auto-merge -- guards against merging an old resolved
    event with a brand new unrelated one that happens to read the same."""
    store = EventStore()
    process_raw_report("Flooding reported in Vijayawada.", datetime(2026, 8, 20, 10, 30), "demo", store)
    r2 = process_raw_report("Flooding reported in Vijayawada.", datetime(2026, 8, 21, 23, 30), "demo", store)
    assert r2["action"] == "CREATE"


def test_false_positive_ignored():
    store = EventStore()
    r = process_raw_report("I watched a movie about a flood.", datetime(2026, 8, 20, 10, 30), "demo", store)
    assert r["action"] == "IGNORED"


def test_location_null_when_absent():
    from nlp_extractor import extract_all
    result = extract_all("Flooding reported in the northern region.")
    assert result["location"] is None


def test_deaths_null_when_absent():
    from nlp_extractor import extract_all
    result = extract_all("Heavy flooding has entered houses near Vijayawada.")
    assert result["deaths"] is None


if __name__ == "__main__":
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__} -- {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
