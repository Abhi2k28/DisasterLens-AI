"""
demo.py
-------
Runs the exact example reports and test cases from the project
spec, in order, and prints output like a jury demo:

    REPORT ARRIVES -> AI/NLP/Event Intelligence -> dashboard change

Run with:  python demo.py
"""

from datetime import datetime, timedelta

from pipeline import process_raw_report
from event_intelligence import EventStore


def line():
    print("-" * 60)


def show_result(i, text, result):
    print(f"\nREPORT {i}: \"{text}\"")
    if result["action"] == "IGNORED":
        print(f"  -> IGNORED ({result['reason']})")
        return
    print(f"  -> ACTION: {result['action']}  |  EVENT: {result['event_id']}")
    print(f"  -> event_confidence: {result['event_confidence']}")
    ev = result["event"]
    print(f"  -> type={ev['disaster_type']} location={ev['location']} "
          f"reports={ev['report_count']} severity={ev['severity']} status={ev['status']}")
    if "match_breakdown" in result and result["match_breakdown"]:
        mb = result["match_breakdown"]
        if "type_score" in mb:
            print(f"     match breakdown: type={mb['type_score']} location={mb['location_score']} "
                  f"time={mb['time_score']} semantic={mb['semantic_score']} -> final={mb['final_score']}")


def main():
    store = EventStore()
    t0 = datetime(2026, 8, 20, 10, 30)

    reports = [
        # (text, minutes_after_t0, source)
        ("Heavy flooding has entered houses near Vijayawada.", 0, "reddit"),
        ("Water entered several homes in Vijayawada due to heavy rain.", 5, "news"),
        ("People are stranded because of flooding in Vijayawada.", 12, "twitter"),
        ("Flooding reported in Visakhapatnam.", 20, "news"),
        ("Fire broke out in a warehouse in Vijayawada.", 25, "reddit"),
        # false positives -- should be IGNORED
        ("I watched a movie about a flood.", 30, "reddit"),
        ("My friend flooded me with messages.", 31, "reddit"),
        ("The earthquake documentary was interesting.", 32, "reddit"),
    ]

    print("=" * 60)
    print("DisasterLens AI -- NLP & Event Intelligence Demo")
    print("=" * 60)

    for i, (text, mins, source) in enumerate(reports, start=1):
        ts = t0 + timedelta(minutes=mins)
        result = process_raw_report(text, ts, source, store)
        show_result(i, text, result)

    line()
    print("\nFINAL DASHBOARD STATE")
    line()
    active = [e for e in store.events.values() if e.status == "ACTIVE"]
    print(f"Active Events: {len(active)}\n")
    for e in store.events.values():
        d = e.to_dict()
        print(f"  {d['event_id']}: {d['disaster_type']} @ {d['location']} "
              f"| reports={d['report_count']} | severity={d['severity']} "
              f"| confidence={d['event_confidence']} | status={d['status']}")


if __name__ == "__main__":
    main()
