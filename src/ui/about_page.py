"""About page: problem statement, team and technologies."""

import streamlit as st


def render(db=None):
    st.title("ℹ️ About the project")
    st.markdown(
        """
**Course:** Advanced Analysis of Algorithms
**Project:** Smart Lost-and-Found Matching System Using String Matching and Dynamic Programming
**Group member:** Noor Ul Ain — CT-046/2024-24

### Problem
In universities, offices and public places, lost and found reports are recorded separately.
Comparing them by hand is slow, especially when people describe the same item with different
words or spelling mistakes. This system compares reports automatically and ranks likely matches.

### Algorithms used
| Algorithm | Role in the system |
|---|---|
| **KMP string matching** | Finds exact keywords and locations in descriptions |
| **Edit distance (Dynamic Programming)** | Handles spelling mistakes, e.g. *walet* ≈ *wallet* |
| **Greedy matching** | Pairs each lost word with the best unused found word |
| **Hash maps** | Keyword index to pick candidate reports quickly |
| **Merge sort** | Ranks candidates from best to worst score |

### Technologies
Python 3 · Streamlit (user interface) · MongoDB (database) · PyMongo

### Limitation
The score is rule-based, not a guaranteed probability. A person should always confirm
ownership with extra details before handing over an item.
"""
    )
