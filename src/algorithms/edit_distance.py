"""
Edit distance (Levenshtein distance) using Dynamic Programming.

dp[i][j] = minimum number of insert / delete / replace operations needed to
           turn the first i letters of `a` into the first j letters of `b`.

Recurrence:
    if a[i-1] == b[j-1]:  dp[i][j] = dp[i-1][j-1]
    else:                 dp[i][j] = 1 + min(dp[i-1][j],    # delete
                                             dp[i][j-1],    # insert
                                             dp[i-1][j-1])  # replace

Time:  O(a * b)      Space: O(a * b)   (a, b = word lengths)
"""


def edit_distance_table(a, b):
    """Build and return the full DP table (used by the UI to show the table)."""
    rows, cols = len(a) + 1, len(b) + 1
    dp = [[0] * cols for _ in range(rows)]

    for i in range(rows):
        dp[i][0] = i  # delete all i letters
    for j in range(cols):
        dp[0][j] = j  # insert all j letters

    for i in range(1, rows):
        for j in range(1, cols):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp


def edit_distance(a, b):
    """Minimum number of single-letter edits to turn `a` into `b`."""
    return edit_distance_table(a, b)[len(a)][len(b)]


def word_similarity(a, b):
    """Convert edit distance into a similarity between 0 (different) and 1 (same)."""
    if not a and not b:
        return 1.0
    return 1 - edit_distance(a, b) / max(len(a), len(b))
