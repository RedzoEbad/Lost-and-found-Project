"""
Unit tests for every algorithm.
Run from the project folder:   python -m unittest discover tests -v
"""

import unittest

from src.algorithms import (
    brute_force_search, build_keyword_index, build_lps, contains_word,
    edit_distance, get_keywords, greedy_word_match, kmp_search, merge_sort,
    word_similarity,
)
from src.matcher import find_matches_for_lost, location_score


class TestKMP(unittest.TestCase):
    def test_lps_table(self):
        self.assertEqual(build_lps("abab"), [0, 0, 1, 2])
        self.assertEqual(build_lps("aaaa"), [0, 1, 2, 3])

    def test_search_positions(self):
        self.assertEqual(kmp_search("abababc", "abc"), [4])
        self.assertEqual(kmp_search("aaaa", "aa"), [0, 1, 2])
        self.assertEqual(kmp_search("hello", "xyz"), [])

    def test_kmp_equals_brute_force(self):
        text = "black wallet and brown wallet near the wall"
        for pattern in ["wallet", "wall", "a", "near the"]:
            self.assertEqual(kmp_search(text, pattern), brute_force_search(text, pattern))

    def test_whole_word(self):
        self.assertTrue(contains_word("Student ID card", "card"))
        self.assertFalse(contains_word("Student ID card", "car"))


class TestEditDistance(unittest.TestCase):
    def test_distances(self):
        self.assertEqual(edit_distance("wallet", "walet"), 1)
        self.assertEqual(edit_distance("kitten", "sitting"), 3)
        self.assertEqual(edit_distance("", "abc"), 3)
        self.assertEqual(edit_distance("same", "same"), 0)

    def test_similarity(self):
        self.assertAlmostEqual(word_similarity("wallet", "walet"), 5 / 6)


class TestGreedyAndHashing(unittest.TestCase):
    def test_greedy_handles_typos(self):
        lost = get_keywords("black leather wallet")
        found_text = "Black lether walet with ID card"
        matches = greedy_word_match(lost, get_keywords(found_text), found_text)
        self.assertEqual([m["found_word"] for m in matches], ["black", "lether", "walet"])

    def test_keyword_index(self):
        index = build_keyword_index([{"id": 1, "description": "red keys"},
                                     {"id": 2, "description": "red bag"}])
        self.assertEqual(index["red"], {1, 2})
        self.assertEqual(index["bag"], {2})


class TestMergeSort(unittest.TestCase):
    def test_sorted_and_stable(self):
        items = [("a", 3), ("b", 1), ("c", 3), ("d", 2)]
        result = merge_sort(items, key=lambda x: x[1])
        self.assertEqual(result, [("a", 3), ("c", 3), ("d", 2), ("b", 1)])  # a before c

    def test_ascending(self):
        self.assertEqual(merge_sort([5, 2, 9, 1], key=lambda x: x, descending=False), [1, 2, 5, 9])


class TestMatcher(unittest.TestCase):
    def test_best_match_first(self):
        found = [
            {"id": 1, "category": "Phone", "description": "Black phone", "location": "Gym",
             "date": "2026-11-02"},
            {"id": 2, "category": "Wallet", "description": "Black lether walet",
             "location": "University library", "date": "2026-11-02"},
        ]
        lost = {"category": "Wallet", "description": "Black leather wallet",
                "location": "Library", "date": "2026-11-01"}
        results, _ = find_matches_for_lost(lost, found)
        self.assertEqual(results[0]["report"]["id"], 2)
        self.assertEqual(results[0]["label"], "Strong match")

    def test_location(self):
        self.assertEqual(location_score("library", "University Library"), 1.0)
        self.assertEqual(location_score("gym", "cafeteria"), 0.0)


if __name__ == "__main__":
    unittest.main()
