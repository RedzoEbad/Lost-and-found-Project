"""Home page: what the system does and how to use it."""

import streamlit as st

from src.ui.components import PAGES, go_to


def render(db):
    st.title("🔎 Smart Lost & Found")
    st.markdown("##### Lost something on campus? Found something? "
                "This system compares reports automatically and shows the most likely matches.")

    counts = db.counts()
    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Found items waiting", counts["found_open"])
    m2.metric("🔍 People still searching", counts["lost_open"])
    m3.metric("✅ Items returned", counts["returned"])

    st.divider()
    st.subheader("How it works")
    steps = [
        ("Describe the item", "Write what it looks like, its category, where and when "
                              "it was lost or found."),
        ("We compare reports", "Words are matched exactly (KMP) or with small spelling "
                               "mistakes (edit distance). Category, place and date are checked too."),
        ("See ranked matches", "Results are sorted best-first (merge sort) with a score out of "
                               "100 and a clear explanation of why each one matched."),
    ]
    cols = st.columns(3)
    for i, (col, (title, text)) in enumerate(zip(cols, steps), start=1):
        col.markdown(
            f"<div class='step-card'><span class='step-num'>{i}</span>"
            f"<h4>{title}</h4><div class='muted'>{text}</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    b1, b2 = st.columns(2)
    b1.button("🔍  I lost something", type="primary", width="stretch",
              on_click=go_to, args=(PAGES[1],))
    b2.button("📦  I found something", width="stretch",
              on_click=go_to, args=(PAGES[2],))

    st.divider()
    st.subheader("How the match score is calculated")
    st.table([
        {"Part": "📝 Description words", "Points": 50,
         "How": "Greedy word matching: exact words via KMP, typos via edit distance"},
        {"Part": "📂 Category", "Points": 20, "How": "Same category = full points"},
        {"Part": "📍 Location", "Points": 20, "How": "Same place = full, sharing words = partial"},
        {"Part": "📅 Date", "Points": 10, "How": "Found within a week after it was lost = full"},
    ])
    st.caption("70+ = Strong match · 45–69 = Possible match · below 45 = Weak match. "
               "Scores are rule-based; always confirm ownership with extra details.")
