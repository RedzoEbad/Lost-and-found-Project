"""
Smart Lost-and-Found Matching System
Entry point. Run with:   streamlit run app.py
"""

import streamlit as st

from src.config import APP_TITLE
from src.ui import about_page, found_page, home, lab_page, lost_page, reports_page
from src.ui.components import PAGES, apply_styles, connection_help, get_database

st.set_page_config(page_title=APP_TITLE, page_icon="🔎", layout="wide")
apply_styles()

RENDERERS = dict(zip(PAGES, [home.render, lost_page.render, found_page.render,
                             reports_page.render, lab_page.render, about_page.render]))
NEEDS_DATABASE = set(PAGES[:4])

db, error = get_database()

with st.sidebar:
    st.markdown(f"## 🔎 {APP_TITLE}")
    st.caption("Match lost and found items using KMP, edit distance, greedy ranking, "
               "hash maps and merge sort.")
    page = st.radio("Go to", PAGES, key="nav", label_visibility="collapsed")
    st.divider()
    if db is not None:
        st.success("Database connected", icon="🟢")
        if st.button("🔄 Refresh data", width="stretch"):
            st.rerun()
    else:
        st.error("Database not connected", icon="🔴")
        if st.button("🔄 Try again", width="stretch"):
            get_database.clear()
            st.rerun()

if page in NEEDS_DATABASE and db is None:
    st.title(page)
    connection_help(error)
else:
    RENDERERS[page](db)
