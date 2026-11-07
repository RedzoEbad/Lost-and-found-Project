"""Shared UI pieces: styling, database connection, navigation and match cards."""

import streamlit as st

from src.config import MONGO_DB_NAME, MONGO_URI, SAMPLE_FOUND_CSV, SAMPLE_LOST_CSV
from src.database import Database

PAGES = [
    "🏠 Home",
    "🔍 I lost something",
    "📦 I found something",
    "📋 All reports",
    "🧪 Algorithm lab",
    "ℹ️ About the project",
]

LABEL_COLORS = {"Strong match": "green", "Possible match": "orange", "Weak match": "gray"}


def apply_styles():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; max-width: 1100px;}
        .step-card {border: 1px solid rgba(128,128,128,.25); border-radius: 12px;
                    padding: 1rem 1.1rem; height: 100%;}
        .step-card h4 {margin: .2rem 0 .4rem 0;}
        .step-num {display:inline-block; width:28px; height:28px; border-radius:50%;
                   background:#2563eb; color:white; text-align:center; line-height:28px;
                   font-weight:700;}
        .muted {opacity: .75; font-size: .92rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner="Connecting to MongoDB...")
def get_database():
    """Connect once and reuse the connection. Returns (db, error_message)."""
    if not MONGO_URI:
        return None, "MONGO_URI is empty. Add your MongoDB link to the .env file."
    try:
        db = Database(MONGO_URI, MONGO_DB_NAME)
        db.ping()
        db.setup(SAMPLE_FOUND_CSV, SAMPLE_LOST_CSV)
        return db, None
    except Exception as exc:  # show any connection problem to the user
        return None, str(exc)


def go_to(page):
    """Button callback to switch page."""
    st.session_state["nav"] = page


def connection_help(error):
    st.error("Could not connect to the MongoDB database.")
    st.code(error[:600])
    st.markdown(
        """
**How to fix it**
1. Open the file **`.env`** in the project folder (copy `.env.example` if it does not exist).
2. Paste your MongoDB link after `MONGO_URI=` , for example
   `MONGO_URI=mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/`
3. In MongoDB Atlas → **Network Access**, add your IP address (or `0.0.0.0/0` for testing).
4. Check the username and password in the link are correct.
5. Stop the app (Ctrl + C) and run it again.

The **Algorithm lab** and **About** pages still work without a database.
"""
    )


def label_badge(label):
    return f":{LABEL_COLORS.get(label, 'gray')}-background[**{label}**]"


def match_card(rank, result, other_side="found"):
    """
    Show one ranked match.
    other_side = "found" when the user lost something (we show found reports),
                 "lost"  when the user found something (we show possible owners).
    """
    report = result["report"]
    score = result["total_score"]
    points = result["points"]

    with st.container(border=True):
        left, right = st.columns([3, 1])
        with left:
            st.markdown(f"#### #{rank} · {report['description']}")
            st.caption(f"📂 {report['category']}  ·  📍 {report['location']}  ·  "
                       f"📅 {report['date']}  ·  {other_side.title()} report #{report['id']}")
        with right:
            st.markdown(label_badge(result["label"]))
            st.markdown(f"### {score * 100:.0f} / 100")

        st.progress(min(score, 1.0))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📝 Description", f"{points['description']:.0f} / 50")
        c2.metric("📂 Category", f"{points['category']:.0f} / 20")
        c3.metric("📍 Location", f"{points['location']:.0f} / 20")
        c4.metric("📅 Date", f"{points['date']:.0f} / 10")

        with st.expander("Why did this match? (step-by-step explanation)"):
            st.markdown("**📝 Description words** — greedy matching with KMP and edit distance")
            for line in result["reasons"]["description"]:
                st.markdown(f"- {line}")
            st.markdown(f"**📂 Category** — {result['reasons']['category']}")
            st.markdown(f"**📍 Location** — {result['reasons']['location']}")
            st.markdown(f"**📅 Date** — {result['reasons']['date']}")

        if report.get("contact"):
            who = "Collect it from / contact" if other_side == "found" else "Owner contact"
            st.info(f"**{who}:** {report['contact']}", icon="📞")
