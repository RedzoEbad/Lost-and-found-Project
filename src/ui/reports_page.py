"""'All reports' page: browse, filter, mark as returned, delete."""

import streamlit as st

from src.algorithms import kmp_search
from src.config import CATEGORIES


def render(db):
    st.title("📋 All reports")
    st.write("Every report stored in the MongoDB database. Use the filters to narrow the list.")

    tab_found, tab_lost = st.tabs(["📦 Found items", "🔍 Lost items"])
    with tab_found:
        report_table(db, "found", db.get_found())
    with tab_lost:
        report_table(db, "lost", db.get_lost())


def report_table(db, kind, reports):
    f1, f2, f3 = st.columns([2, 1, 1])
    text = f1.text_input("Search in descriptions (uses KMP)", key=f"q_{kind}",
                         placeholder="e.g. wallet")
    category = f2.selectbox("Category", ["All"] + CATEGORIES, key=f"c_{kind}")
    status = f3.selectbox("Status", ["All", "Open", "Returned"], key=f"s_{kind}")

    rows = [
        r for r in reports
        if (category == "All" or r["category"] == category)
        and (status == "All" or r["status"] == status)
        and (not text.strip() or kmp_search(r["description"], text))
    ]

    st.caption(f"Showing {len(rows)} of {len(reports)} {kind} reports")
    if not rows:
        st.info("No reports match these filters.")
        return

    st.dataframe(
        [{"Report #": r["id"], "Status": ("✅ " if r["status"] == "Returned" else "🟡 ") + r["status"],
          "Category": r["category"], "Description": r["description"],
          "Location": r["location"], "Date": r["date"], "Contact": r["contact"]} for r in rows],
        width="stretch", hide_index=True,
    )

    with st.expander("⚙️ Manage a report"):
        numbers = [r["id"] for r in rows]
        chosen = st.selectbox("Choose report #", numbers, key=f"m_{kind}")
        a, b, c = st.columns([1, 1, 2])
        if a.button("✅ Mark returned", key=f"ret_{kind}"):
            db.set_status(kind, chosen, "Returned")
            st.toast(f"Report #{chosen} marked as returned")
            st.rerun()
        if b.button("↩️ Mark open", key=f"open_{kind}"):
            db.set_status(kind, chosen, "Open")
            st.rerun()
        sure = c.checkbox("Yes, delete it permanently", key=f"sure_{kind}")
        if c.button("🗑️ Delete", key=f"del_{kind}", disabled=not sure):
            db.delete(kind, chosen)
            st.toast(f"Report #{chosen} deleted")
            st.rerun()
