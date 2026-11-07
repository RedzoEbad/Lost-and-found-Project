"""
Matching pipeline: combines all algorithms to rank potential matches.

Steps
  1. Hash-map index  -> pick candidates (share a keyword OR same category)
  2. Greedy + KMP + edit distance -> score each candidate
  3. Merge sort -> rank candidates by score

Score out of 100 points:
  Description words 50  |  Category 20  |  Location 20  |  Date 10
"""

from datetime import date

from src.algorithms import (
    build_keyword_index, build_report_map, get_keywords, greedy_word_match,
    kmp_search, merge_sort,
)

WEIGHTS = {"description": 0.50, "category": 0.20, "location": 0.20, "date": 0.10}
STRONG_MATCH = 0.70
POSSIBLE_MATCH = 0.45


# ---------- individual scores ----------
def description_keywords(report):
    """Description words, without words that belong to the location (scored separately)."""
    location_words = set(get_keywords(report.get("location", "")))
    return [w for w in get_keywords(report["description"]) if w not in location_words]


def location_score(lost_location, found_location):
    """1.0 if one location contains the other (KMP), otherwise shared-word ratio."""
    if not lost_location.strip() or not found_location.strip():
        return 0.0
    if kmp_search(found_location, lost_location) or kmp_search(lost_location, found_location):
        return 1.0
    lost_set = set(get_keywords(lost_location))
    found_set = set(get_keywords(found_location))
    if not lost_set:
        return 0.0
    return len(lost_set & found_set) / len(lost_set)


def date_score(lost_date, found_date):
    """Items are usually found soon after being lost; found *before* lost is unlikely."""
    try:
        days = (date.fromisoformat(found_date) - date.fromisoformat(lost_date)).days
    except (TypeError, ValueError):
        return 0.5, "Date unknown, so this part is neutral."
    if days < -1:
        return 0.0, f"Reported found {abs(days)} days before it was lost (unlikely)."
    if days <= 7:
        return 1.0, f"Found {max(days, 0)} day(s) after it was lost."
    if days <= 30:
        return 0.5, f"Found {days} days after it was lost."
    return 0.2, f"Found {days} days after it was lost (long gap)."


def get_label(score):
    if score >= STRONG_MATCH:
        return "Strong match"
    if score >= POSSIBLE_MATCH:
        return "Possible match"
    return "Weak match"


# ---------- full score for one pair ----------
def score_report(lost, found):
    lost_words = description_keywords(lost)
    found_words = description_keywords(found)
    matches = greedy_word_match(lost_words, found_words, found["description"])

    desc = sum(m["similarity"] for m in matches) / len(lost_words) if lost_words else 0.0
    cat = 1.0 if lost["category"].lower() == found["category"].lower() else 0.0
    loc = location_score(lost["location"], found["location"])
    day, date_reason = date_score(lost.get("date"), found.get("date"))

    parts = {"description": desc, "category": cat, "location": loc, "date": day}
    points = {k: v * WEIGHTS[k] * 100 for k, v in parts.items()}
    total = sum(v * WEIGHTS[k] for k, v in parts.items())

    reasons = {
        "description": _describe_words(matches, lost_words),
        "category": (f"Both are in the '{found['category']}' category." if cat
                     else f"Different categories ('{lost['category']}' vs '{found['category']}')."),
        "location": _describe_location(loc, lost["location"], found["location"]),
        "date": date_reason,
    }
    return {
        "lost": lost, "found": found, "matches": matches,
        "parts": parts, "points": points, "reasons": reasons,
        "total_score": total, "label": get_label(total),
    }


def _describe_words(matches, lost_words):
    if not matches:
        return ["No matching words in the descriptions."]
    lines = []
    for m in matches:
        if m["distance"] == 0:
            lines.append(f"'{m['lost_word']}' appears exactly (found with KMP).")
        else:
            lines.append(f"'{m['lost_word']}' ≈ '{m['found_word']}': {m['distance']} letter(s) "
                         f"different, {m['similarity'] * 100:.0f}% similar (edit distance).")
    lines.append(f"{len(matches)} of {len(lost_words)} important words matched.")
    return lines


def _describe_location(score, lost_loc, found_loc):
    if score == 1.0:
        return f"Same place: '{lost_loc}' and '{found_loc}'."
    if score > 0:
        return f"Partly the same place: '{lost_loc}' and '{found_loc}' share some words."
    return f"Different places: '{lost_loc}' vs '{found_loc}'."


# ---------- ranking ----------
def _rank(query, candidates, query_is_lost, top_k):
    index = build_keyword_index(candidates)
    report_map = build_report_map(candidates)

    candidate_ids = set()
    for word in get_keywords(query["description"]):
        candidate_ids |= index.get(word, set())
    for report in candidates:
        if report["category"].lower() == query["category"].lower():
            candidate_ids.add(report["id"])

    results = []
    for cid in candidate_ids:
        other = report_map[cid]
        pair = score_report(query, other) if query_is_lost else score_report(other, query)
        pair["report"] = other
        results.append(pair)

    ranked = merge_sort(results, key=lambda r: r["total_score"])
    return ranked[:top_k], len(candidate_ids)


def find_matches_for_lost(lost, found_items, top_k=5):
    """Someone lost something: rank found-item reports."""
    return _rank(lost, found_items, query_is_lost=True, top_k=top_k)


def find_matches_for_found(found, lost_items, top_k=3):
    """Someone found something: rank lost-item reports (possible owners)."""
    return _rank(found, lost_items, query_is_lost=False, top_k=top_k)
