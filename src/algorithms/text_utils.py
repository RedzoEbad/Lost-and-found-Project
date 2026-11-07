"""
Text cleaning helpers used by every other algorithm.

normalize_text  -> lower-case, remove punctuation, collapse spaces   O(n)
get_keywords    -> important words only (stop words removed)        O(n)
"""

import re

# Common words that carry no meaning when comparing two item descriptions
STOP_WORDS = {
    "a", "an", "the", "and", "or", "of", "in", "on", "at", "near", "to", "is",
    "was", "it", "its", "my", "me", "i", "with", "from", "for", "by", "lost",
    "found", "outside", "inside", "item", "some", "this", "that", "has", "have",
    "had", "there", "here", "around", "into", "be", "been", "which", "very",
}


def normalize_text(text):
    """Lower-case the text and replace punctuation with spaces."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def tokenize(text):
    """Split normalized text into words."""
    return normalize_text(text).split()


def get_keywords(text):
    """Return the meaningful words of a text, without duplicates, in original order."""
    keywords = []
    for word in tokenize(text):
        if word not in STOP_WORDS and word not in keywords:
            keywords.append(word)
    return keywords
