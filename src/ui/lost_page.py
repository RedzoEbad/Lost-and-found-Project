"""'I lost something' page: describe the item, search found reports, optionally save."""

import time
from datetime import date

import streamlit as st

from src.config import CATEGORIES
from src.matcher import POSSIBLE_MATCH, find_matches_for_lost
from src.ui.components import match_card


def render(db):
    st.title("🔍 I lost something")
    st.write("Fill in the details below. The more specific you are (colour, brand, "
             "material), the better the matches.")

    with st.form("lost_form"):
        description = st.text_area(
            "1️⃣  What did you lose? *",
            placeholder="e.g. Black leather wallet with my student card",
            help="Colour, brand, material and what was inside help the most.",
        )
        c1, c2, c3 = st.columns(3)
        category = c1.selectbox("2️⃣  Category *", CATEGORIES)
        location = c2.text_input("3️⃣  Where did you lose it? *", placeholder="e.g. University library")
        lost_date = c3.date_input("4️⃣  When did you lose it?", value=date.today(),
                                  max_value=date.today())
        clues = st.text_input("Extra identifying clues (optional)",
                              placeholder="e.g. red sticker on the back, name written inside")

        st.markdown("**Save my report** so that if someone finds it later, they can see it.")
        s1, s2 = st.columns([2, 1])
        contact = s1.text_input("Your email or phone (needed only if you save)")
        save = s2.checkbox("Save my report", value=True)

        submitted = st.form_submit_button("🔎  Search for my item", type="primary",
                                          width="stretch")

    if submitted:
        if not description.strip() or not location.strip():
            st.error("Please fill in the description and the location.")
            return

        lost = {
            "description": f"{description} {clues}".strip(),
            "category": category,
            "location": location,
            "date": lost_date.isoformat(),
            "contact": contact,
        }
        start = time.perf_counter()
        results, checked = find_matches_for_lost(lost, db.get_found(status="Open"), top_k=5)
        elapsed = (time.perf_counter() - start) * 1000

        saved_no = None
        if save:
            if contact.strip():
                saved_no = db.add_lost(lost)
            else:
                st.warning("Your report was not saved because no contact was given.")

        st.session_state["lost_results"] = (results, checked, elapsed, saved_no)

    if "lost_results" in st.session_state:
        show_results(*st.session_state["lost_results"])


def show_results(results, checked, elapsed, saved_no):
    st.divider()
    st.subheader("Results")
    if saved_no:
        st.success(f"Your report was saved as **Lost report #{saved_no}**.", icon="💾")

    good = [r for r in results if r["total_score"] >= POSSIBLE_MATCH]
    if good:
        st.success(f"🎉 We found **{len(good)}** promising match(es). The best one is shown first.")
    elif results:
        st.warning("No strong matches yet. Below are the closest reports. "
                   "Try adding more details, or check again later.")
    else:
        st.info("No found-item reports share anything with your description yet.")

    st.caption(f"Compared with {checked} candidate report(s) picked by the hash-map index "
               f"in {elapsed:.1f} ms.")

    for rank, result in enumerate(results, start=1):
        match_card(rank, result, other_side="found")
