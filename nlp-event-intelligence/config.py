"""
config.py
---------
Central place for keyword lists, the known-places list, and the
event-matching threshold.

Keeping these here (instead of scattered inside logic files) means
you can tune the system fast during the hackathon without hunting
through code.
"""

# ---------------------------------------------------------------
# Disaster type keywords
# NOTE: In the real architecture, disaster classification is the
# AI/ML teammate's job. This dictionary is only a TEMPORARY stand-in
# so the NLP + Event Intelligence pipeline can be demoed end-to-end
# before AI/ML hands off their classifier. Swap it out once their
# module is ready (see nlp_extractor.classify_disaster_type_stub).
# ---------------------------------------------------------------
DISASTER_KEYWORDS = {
    "FLOOD": ["flood", "flooding", "flooded", "water entered", "waterlogged", "inundated"],
    "FIRE": ["fire", "blaze", "burning", "wildfire"],
    "EARTHQUAKE": ["earthquake", "quake", "tremor", "seismic"],
    "CYCLONE": ["cyclone", "storm", "hurricane", "typhoon"],
    "LANDSLIDE": ["landslide", "mudslide", "rockslide"],
}

# Phrases that indicate the sentence is NOT a real disaster report
# (movies, casual speech, metaphors) -- used only for the demo
# stub classifier's false-positive test cases.
NON_EVENT_HINTS = [
    "movie", "film", "documentary", "flooded me with messages",
    "game", "novel", "song", "flooded with emails", "flooded with calls",
]

# ---------------------------------------------------------------
# A small known-places gazetteer.
# For the MVP we don't call any geocoding API (no reliable internet
# on the dev machine), so we validate extracted locations against
# this list when possible. If a place isn't in the list, we still
# keep whatever the regex extracted -- we just mark it "unverified".
# Extend this list with places relevant to your demo script.
# ---------------------------------------------------------------
KNOWN_PLACES = [
    "Vijayawada", "Visakhapatnam", "Guntur", "Vizag", "Amaravati",
    "Tirupati", "Kakinada", "Rajahmundry", "Nellore", "Kurnool",
    "Chennai", "Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Kolkata",
]

# ---------------------------------------------------------------
# Impact keyword map: keyword -> field it sets to True
# ---------------------------------------------------------------
IMPACT_KEYWORDS = {
    "houses_affected": ["houses", "homes", "residences", "buildings damaged", "houses damaged"],
    "people_affected": ["people affected", "residents affected", "families affected"],
    "people_stranded": ["stranded", "trapped", "cut off"],
    "road_blocked": ["road blocked", "roads blocked", "road closed", "highway blocked"],
    "evacuation": ["evacuate", "evacuated", "evacuation"],
    "infrastructure_damage": ["bridge damaged", "infrastructure damaged", "power lines down", "collapsed"],
}

# ---------------------------------------------------------------
# Event matching threshold.
#
# WHY 0.60 (see README.md "Threshold Reasoning" for the worked
# examples that justify this number):
#   - Two reports about the SAME event, same city, close in time,
#     with reworded but similar text typically score 0.70-0.95.
#   - Two reports about DIFFERENT events (different city, or
#     different disaster type) typically score 0.10-0.45.
#   - 0.60 sits in the gap between those clusters, so it separates
#     them cleanly on our test cases without being so strict that
#     minor wording differences create duplicate events.
# ---------------------------------------------------------------
MATCH_THRESHOLD = 0.60

# How many hours apart before we stop treating two reports as
# possibly-the-same ongoing event, regardless of other similarity.
TIME_WINDOW_HOURS = 12

# Scoring weights (must sum to 1.0). See README for rationale.
WEIGHTS = {
    "type": 0.30,
    "location": 0.30,
    "time": 0.15,
    "semantic": 0.25,
}
