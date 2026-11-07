"""
String matching algorithms.

1. Knuth-Morris-Pratt (KMP)   -> O(n + m) time, O(m) extra space
2. Brute force (naive)        -> O(n * m) worst case (used only as a baseline
                                 for the speed comparison in the Algorithm Lab)

n = length of the text, m = length of the pattern.
Both functions accept an optional `stats` dict; if given, the number of
character comparisons is stored in stats["comparisons"].
"""

from .text_utils import normalize_text


def build_lps(pattern):
    """
    Build the LPS table (Longest proper Prefix that is also a Suffix).
    lps[i] = length of the longest proper prefix of pattern[0..i]
             that is also a suffix of pattern[0..i].
    Time: O(m)
    """
    lps = [0] * len(pattern)
    length = 0  # length of the previous longest prefix-suffix
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]  # fall back inside the pattern, do not move i
        else:
            lps[i] = 0
            i += 1
    return lps


def kmp_search(text, pattern, normalize=True, stats=None):
    """
    Return every starting index where `pattern` occurs in `text`.
    The text pointer never moves backwards, which gives O(n + m).
    """
    if normalize:
        text, pattern = normalize_text(text), normalize_text(pattern)
    if not pattern:
        return []

    lps = build_lps(pattern)
    positions = []
    comparisons = 0
    i = j = 0  # i -> index in text, j -> index in pattern
    while i < len(text):
        comparisons += 1
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):  # complete match
                positions.append(i - j)
                j = lps[j - 1]
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1

    if stats is not None:
        stats["comparisons"] = comparisons
    return positions


def brute_force_search(text, pattern, normalize=True, stats=None):
    """Naive search: try every starting position. O(n * m) worst case."""
    if normalize:
        text, pattern = normalize_text(text), normalize_text(pattern)
    n, m = len(text), len(pattern)
    positions = []
    comparisons = 0
    if m == 0:
        return positions
    for start in range(n - m + 1):
        k = 0
        while k < m:
            comparisons += 1
            if text[start + k] != pattern[k]:
                break
            k += 1
        if k == m:
            positions.append(start)

    if stats is not None:
        stats["comparisons"] = comparisons
    return positions


def contains_word(text, word):
    """
    True if `word` appears in `text` as a WHOLE word.
    Spaces are added around both so 'car' does not match inside 'card'.
    """
    padded_text = " " + normalize_text(text) + " "
    padded_word = " " + normalize_text(word) + " "
    return len(kmp_search(padded_text, padded_word, normalize=False)) > 0
