"""'I found something' page: save a found report and show possible owners."""

from datetime import date

import streamlit as st

from src.config import CATEGORIES
from src.matcher import find_matches_for_found
from src.ui.components import match_card


def render(db):
    st.title("📦 I found something")
    st.write("Thank you for helping! Describe the item and where you found it. "
             "We will save it and immediately check if someone has reported it lost.")

    with st.form("found_form", clear_on_submit=True):
        description = st.text_area("1️⃣  What did you find? *",
                                   placeholder="e.g. Brown leather wallet with some cash")
        c1, c2, c3 = st.columns(3)
        category = c1.selectbox("2️⃣  Category *", CATEGORIES)
        location = c2.text_input("3️⃣  Where did you find it? *", placeholder="e.g. Bus stop")
        found_date = c3.date_input("4️⃣  When did you find it?", value=date.today(),
                                   max_value=date.today())
        contact = st.text_input("Where can the owner collect it? *",
                                value="Lost & Found office",
                                help="Your email/phone, or the office where you handed it in.")
        submitted = st.form_submit_button("💾  Save found item", type="primary",
                                          width="stretch")

    if submitted:
        if not description.strip() or not location.strip() or not contact.strip():
            st.error("Please fill in all fields marked with *.")
            return
        found = {"description": description, "category": category, "location": location,
                 "date": found_date.isoformat(), "contact": contact}
        report_no = db.add_found(found)
        results, _ = find_matches_for_found(found, db.get_lost(status="Open"), top_k=3)
        st.session_state["found_results"] = (report_no, results)

    if "found_results" in st.session_state:
        report_no, results = st.session_state["found_results"]
        st.divider()
        st.success(f"Saved as **Found report #{report_no}**. Thank you!", icon="✅")
        st.subheader("People who may have lost this item")
        if results:
            st.caption("These lost reports look similar. You can contact the owner directly.")
            for rank, result in enumerate(results, start=1):
                match_card(rank, result, other_side="lost")
        else:
            st.info("Nobody has reported a similar lost item yet. "
                    "When someone does, your report will show up in their search.")
