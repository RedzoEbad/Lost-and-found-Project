"""
Greedy word matching.

For each word in the lost description (in order) we make the locally best
choice: the most similar found-description word that has not been used yet.
  * Exact whole-word match is checked first with KMP.
  * Otherwise edit distance (DP) is used to accept small spelling mistakes.

Time: O(L * F * C)
  L = words in lost description, F = words in found description,
  C = cost of comparing two words with edit distance (O(word length^2)).
"""

from .edit_distance import edit_distance
from .kmp import contains_word

SIMILARITY_THRESHOLD = 0.75  # e.g. "walet" vs "wallet" = 0.83 -> accepted


def greedy_word_match(lost_words, found_words, found_text, threshold=SIMILARITY_THRESHOLD):
    used = set()
    matches = []

    for lost_word in lost_words:
        # 1) Exact match, found with KMP
        if lost_word not in used and contains_word(found_text, lost_word):
            used.add(lost_word)
            matches.append({
                "lost_word": lost_word, "found_word": lost_word,
                "similarity": 1.0, "distance": 0, "method": "exact (KMP)",
            })
            continue

        # 2) Greedy choice: most similar unused word
        best_word, best_sim, best_dist = None, 0.0, None
        for found_word in found_words:
            if found_word in used:
                continue
            dist = edit_distance(lost_word, found_word)
            sim = 1 - dist / max(len(lost_word), len(found_word))
            if sim > best_sim:
                best_word, best_sim, best_dist = found_word, sim, dist

        if best_word is not None and best_sim >= threshold:
            used.add(best_word)
            matches.append({
                "lost_word": lost_word, "found_word": best_word,
                "similarity": best_sim, "distance": best_dist,
                "method": "similar spelling (edit distance)",
            })

    return matches
