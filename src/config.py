"""Project settings. The MongoDB link is read from the .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI", "").strip()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "lost_and_found").strip() or "lost_and_found"

DATA_DIR = BASE_DIR / "data"
SAMPLE_FOUND_CSV = DATA_DIR / "sample_found_items.csv"
SAMPLE_LOST_CSV = DATA_DIR / "sample_lost_items.csv"

APP_TITLE = "Smart Lost & Found"

CATEGORIES = [
    "Wallet", "Phone", "Keys", "Bag", "Bottle", "Electronics", "Glasses",
    "Jewellery", "Books", "Umbrella", "Watch", "ID Card", "Clothing", "Other",
]
