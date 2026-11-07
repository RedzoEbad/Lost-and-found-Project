"""Algorithm lab: try each algorithm on its own and compare performance (for the report)."""

import random
import time

import streamlit as st

from src.algorithms import (
    brute_force_search, build_lps, edit_distance_table, kmp_search, merge_sort,
    normalize_text, word_similarity,
)


def render(db=None):
    st.title("🧪 Algorithm lab")
    st.write("See each algorithm working step by step. Useful for understanding "
             "and for screenshots in the report.")

    t1, t2, t3, t4, t5 = st.tabs(["KMP search", "Edit distance", "Merge sort",
                                  "KMP vs Brute force", "Complexity"])
    with t1:
        kmp_demo()
    with t2:
        edit_distance_demo()
    with t3:
        merge_sort_demo()
    with t4:
        speed_comparison()
    with t5:
        complexity_table()


def kmp_demo():
    st.subheader("Knuth–Morris–Pratt (KMP) string search")
    st.caption("KMP first builds an LPS table from the pattern, so when a mismatch happens "
               "it never re-checks text characters it has already seen.")
    text = st.text_area("Text", "Black leather wallet found near the library, wallet has a card")
    pattern = st.text_input("Pattern to find", "wallet")

    clean_pattern = normalize_text(pattern)
    if not clean_pattern:
        st.info("Type a pattern.")
        return

    lps = build_lps(clean_pattern)
    st.markdown("**Step 1 — LPS table of the pattern**")
    lps_row = {"": "LPS value"}
    for i, ch in enumerate(clean_pattern):
        lps_row[f"{i}: '{ch}'"] = str(lps[i])
    st.dataframe([lps_row], hide_index=True)
    st.caption("Column = position and character of the pattern. LPS tells KMP how far "
               "it can jump back inside the pattern after a mismatch.")

    kmp_stats, brute_stats = {}, {}
    positions = kmp_search(text, pattern, stats=kmp_stats)
    brute_force_search(text, pattern, stats=brute_stats)

    st.markdown("**Step 2 — Search result**")
    clean_text = normalize_text(text)
    if positions:
        highlighted, last = "", 0
        for p in positions:
            highlighted += clean_text[last:p] + f":blue-background[**{clean_text[p:p + len(clean_pattern)]}**]"
            last = p + len(clean_pattern)
        highlighted += clean_text[last:]
        st.markdown(highlighted)
        st.success(f"Found {len(positions)} time(s) at positions {positions}")
    else:
        st.warning("Pattern not found.")

    c1, c2 = st.columns(2)
    c1.metric("KMP character comparisons", kmp_stats.get("comparisons", 0))
    c2.metric("Brute-force character comparisons", brute_stats.get("comparisons", 0))


def edit_distance_demo():
    st.subheader("Edit distance (Dynamic Programming)")
    st.caption("Counts the minimum number of letter insertions, deletions or replacements "
               "to turn one word into another. This is how spelling mistakes are handled.")
    c1, c2 = st.columns(2)
    a = normalize_text(c1.text_input("Word 1", "wallet")).replace(" ", "")
    b = normalize_text(c2.text_input("Word 2", "walet")).replace(" ", "")

    table = edit_distance_table(a, b)
    # Column names include the position so repeated letters (e.g. the two l's) stay unique
    header = ["Word 1 ↓ / Word 2 →", "ε"] + [f"{j + 1}:{ch}" for j, ch in enumerate(b)]
    rows = []
    for i, row in enumerate(table):
        label = "ε" if i == 0 else f"{i}:{a[i - 1]}"
        rows.append(dict(zip(header, [label] + row)))
    st.markdown("**DP table** — each cell = edits needed for those prefixes. "
                "The bottom-right cell is the answer.")
    st.dataframe(rows, hide_index=True)

    distance = table[len(a)][len(b)]
    sim = word_similarity(a, b)
    m1, m2, m3 = st.columns(3)
    m1.metric("Edit distance", distance)
    m2.metric("Similarity", f"{sim * 100:.0f}%")
    m3.metric("Counted as a match?", "Yes ✅" if sim >= 0.75 else "No ❌")
    st.caption("The system treats two words as matching when similarity is 75% or more.")


def merge_sort_demo():
    st.subheader("Merge sort (ranking results)")
    st.caption("Splits the list in half, sorts each half, then merges them. "
               "Always O(k log k) and stable.")
    raw = st.text_input("Match scores (comma separated)", "45, 88, 12, 67, 88, 30, 95")
    try:
        values = [float(x) for x in raw.split(",") if x.strip()]
    except ValueError:
        st.error("Please type numbers separated by commas.")
        return
    items = [{"report": f"R{i + 1}", "score": v} for i, v in enumerate(values)]
    ranked = merge_sort(items, key=lambda x: x["score"])
    c1, c2 = st.columns(2)
    c1.markdown("**Before**")
    c1.dataframe(items, hide_index=True)
    c2.markdown("**After merge sort (best first)**")
    c2.dataframe(ranked, hide_index=True)
    st.caption("Equal scores keep their original order — this is what 'stable' means.")


def speed_comparison():
    st.subheader("KMP vs Brute force — performance comparison")
    st.caption("Worst-case style input: text 'aaaa…a' with pattern 'aaa…ab'. "
               "Brute force re-checks characters; KMP does not.")
    pattern_len = st.slider("Pattern length", 5, 50, 20)
    mode = st.radio("Text type", ["Worst case (aaaa…)", "Random letters"], horizontal=True)

    if st.button("▶️ Run comparison", type="primary"):
        pattern = "a" * (pattern_len - 1) + "b"
        rows = []
        for n in [1000, 5000, 10000, 20000, 40000]:
            if mode.startswith("Worst"):
                text = "a" * n
            else:
                text = "".join(random.choice("ab") for _ in range(n))
            ks, bs = {}, {}
            t0 = time.perf_counter()
            kmp_search(text, pattern, normalize=False, stats=ks)
            t1 = time.perf_counter()
            brute_force_search(text, pattern, normalize=False, stats=bs)
            t2 = time.perf_counter()
            rows.append({"Text length": n,
                         "KMP comparisons": ks["comparisons"],
                         "Brute-force comparisons": bs["comparisons"],
                         "KMP time (ms)": round((t1 - t0) * 1000, 2),
                         "Brute-force time (ms)": round((t2 - t1) * 1000, 2)})
        st.dataframe(rows, hide_index=True, width="stretch")
        st.line_chart({"KMP": [r["KMP comparisons"] for r in rows],
                       "Brute force": [r["Brute-force comparisons"] for r in rows]},
                      x_label="Test (increasing text length)", y_label="Character comparisons")
        st.caption("KMP grows linearly with text length (n + m). Brute force grows with n × m.")


def complexity_table():
    st.subheader("Complexity summary")
    st.table([
        {"Algorithm": "KMP search", "Time": "O(n + m)", "Space": "O(m)",
         "Used for": "Exact keyword & location matching"},
        {"Algorithm": "Brute-force search", "Time": "O(n × m) worst", "Space": "O(1)",
         "Used for": "Baseline for comparison"},
        {"Algorithm": "Edit distance (DP)", "Time": "O(a × b)", "Space": "O(a × b)",
         "Used for": "Spelling mistakes"},
        {"Algorithm": "Greedy word matching", "Time": "O(L × F × C)", "Space": "O(L)",
         "Used for": "Pairing words of two descriptions"},
        {"Algorithm": "Hash-map index", "Time": "O(1) avg lookup", "Space": "O(total words)",
         "Used for": "Picking candidate reports quickly"},
        {"Algorithm": "Merge sort", "Time": "O(k log k)", "Space": "O(k)",
         "Used for": "Ranking candidates by score"},
    ])
    st.caption("n = text length, m = pattern length, a/b = word lengths, L/F = word counts, "
               "C = cost of one word comparison, k = number of candidates.")
