"""
Hash-map based structures (Python dict = hash table).

build_keyword_index : keyword -> set of report IDs  (an inverted index)
build_report_map    : report ID -> report

Building: O(total words).  Lookup: O(1) on average.
The keyword index lets us skip reports that share nothing with the query,
instead of comparing the query against every report in the database.
"""

from .text_utils import get_keywords


def build_keyword_index(reports):
    index = {}
    for report in reports:
        for word in get_keywords(report["description"]):
            index.setdefault(word, set()).add(report["id"])
    return index


def build_report_map(reports):
    return {report["id"]: report for report in reports}
