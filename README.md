# Smart Lost-and-Found Matching System

**Advanced Analysis of Algorithms — Project**
Noor Ul Ain — CT-046/2024-24

The system compares lost-item and found-item reports and ranks the most likely matches.
It uses **KMP string matching**, **Edit distance (Dynamic Programming)**, **Greedy matching**,
**Hash maps** and **Merge sort**. Reports are stored in **MongoDB** and the interface is built
with **Streamlit**.

---

## 1. Setup (one time)

### Windows (easiest)
1. Unzip the project folder.
2. Double-click **`setup.bat`**. It creates a virtual environment and installs everything.
3. Open the **`.env`** file with Notepad and paste your MongoDB link:
   ```
   MONGO_URI=mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/
   MONGO_DB_NAME=lost_and_found
   ```
4. Double-click **`run.bat`**. The app opens in your browser at http://localhost:8501

### Any system (manual)
```bash
cd LostAndFoundMatcher
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux
pip install -r requirements.txt
python -m streamlit run app.py
```

### MongoDB Atlas checklist
- **Database Access:** create a database user; use its username and password in the link.
- **Network Access:** add your IP address (or `0.0.0.0/0` while testing).
- If your password contains special characters like `@` or `#`, URL-encode them
  (`@` → `%40`, `#` → `%23`).

On the first run the app automatically creates the collections and loads
22 sample found items and 8 sample lost items from the `data/` folder.

---

## 2. Using the app

| Page | What it does |
|---|---|
| 🏠 Home | Overview, live counts, how the score works |
| 🔍 I lost something | Describe a lost item → ranked found reports with an explanation |
| 📦 I found something | Save a found item → shows people who may have lost it |
| 📋 All reports | Browse/filter reports (KMP search), mark as returned, delete |
| 🧪 Algorithm lab | Step-by-step demos: LPS table, DP table, merge sort, KMP vs brute force chart |
| ℹ️ About | Problem statement and team |

### Match score (out of 100)
| Part | Points | Method |
|---|---|---|
| Description words | 50 | Greedy matching: exact words with KMP, typos with edit distance |
| Category | 20 | Same category |
| Location | 20 | KMP containment / shared words |
| Date | 10 | Found within a week after being lost |

70+ Strong · 45–69 Possible · below 45 Weak

---

## 3. Project structure
```
LostAndFoundMatcher/
├── app.py                     # entry point (streamlit run app.py)
├── requirements.txt
├── .env / .env.example        # MongoDB link goes here
├── setup.bat / run.bat        # Windows helpers
├── data/
│   ├── sample_found_items.csv
│   └── sample_lost_items.csv
├── src/
│   ├── config.py              # settings
│   ├── database.py            # MongoDB layer (PyMongo)
│   ├── matcher.py             # scoring + ranking pipeline
│   ├── algorithms/
│   │   ├── text_utils.py      # cleaning, keywords
│   │   ├── kmp.py             # KMP + brute force
│   │   ├── edit_distance.py   # DP edit distance
│   │   ├── hashing.py         # hash-map keyword index
│   │   ├── greedy.py          # greedy word matching
│   │   └── merge_sort.py      # merge sort ranking
│   └── ui/                    # one file per page
└── tests/
    └── test_algorithms.py
```

## 4. Run the tests
```bash
python -m unittest discover tests -v
```

## 5. Complexity
| Algorithm | Time | Space |
|---|---|---|
| KMP | O(n + m) | O(m) |
| Brute force (baseline) | O(n·m) worst | O(1) |
| Edit distance | O(a·b) | O(a·b) |
| Greedy word matching | O(L·F·C) | O(L) |
| Hash-map lookup | O(1) average | O(total words) |
| Merge sort | O(k log k) | O(k) |

Overall, for one search over R reports: building the index is O(total words); each of the
k candidates costs O(L·F·C); ranking costs O(k log k).
