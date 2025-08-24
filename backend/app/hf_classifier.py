import os
import requests
from dotenv import load_dotenv
import re

from .db import db
from datetime import datetime, timedelta, timezone


load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

# Hugging Face model
HF_MODEL = "facebook/bart-large-mnli"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# Mapping keywords/synonyms to your categories
CATEGORY_MAP = {
    "Food": ["food", "breakfast", "lunch", "dinner", "snacks", "meal", "restaurant"],
    "Petrol": ["petrol", "fuel", "gas", "diesel"],
    "Rent": ["rent", "pg", "apartment"],
    "Electricity": ["eb", "elec", "electricity", "bill", "ebill", "elec bill"],
    "Outing": ["outing", "trip", "hangout", "friends"],
    "Movies": ["movie", "cinema", "theater", "film"],
    "Bike Service": ["service", "bike service", "repair", "maintenance"],
    "Savings": ["save", "savings"],
    "SIP": ["sip", "mutual fund", "mf"],
    "Stocks": ["stocks", "share", "equity", "investment"],
    "Shopping": ["shopping", "dress", "shirt", "pants", "shoes", "slippers", "clothes", "jacket", "shopping", "apparel", "bag", "accessory", "tshirt", "sneakers", "sandals", "jeans", "skirt", "hat", "watch"
]
}

def classify_expense(text: str) -> str:
    text_lower = text.lower()

    # First, check keywords in CATEGORY_MAP
    for category, keywords in CATEGORY_MAP.items():
        if any(kw in text_lower for kw in keywords):
            return category

    # Fallback to Hugging Face zero-shot classification
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": list(CATEGORY_MAP.keys())}
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        if "labels" in result and len(result["labels"]) > 0:
            return result["labels"][0]
        return "Wants"
    else:
        raise Exception(f"HF API Error {response.status_code}: {response.text}")
    
def parse_query(text: str):
    """
    Extract categories from a user query for listing expenses.
    Returns a dict: {"categories": [...], "text": lowercased_text}
    """
    text_lower = text.lower()
    found_categories = []
    for category, keywords in CATEGORY_MAP.items():
        if any(kw in text_lower for kw in keywords):
            found_categories.append(category)
    return {"categories": found_categories, "text": text_lower}

def extract_amount(text: str) -> float:
    """
    Extract the first number (integer or decimal) from a text string.
    Returns 0.0 if no number is found.
    Examples:
        "550rs lunch" -> 550.0
        "100.5 dinner" -> 100.5
    """
    text_clean = text.replace(",", "").lower()
    match = re.search(r"\d+(\.\d+)?", text_clean)
    return float(match.group()) if match else 0.0




from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def parse_relative_date_calendar(text: str):
    """
    Parse phrases like 'last week', 'last month', 'last 2 months', 'this month'
    Returns start_date and end_date as datetime objects (UTC)
    """
    text = text.lower()
    now = datetime.utcnow()
    start_date = end_date = None

    # This month
    if "this month" in text:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = (start_date + relativedelta(months=1)) - timedelta(seconds=1)
        return start_date, end_date

    # Last month
    if "last month" in text:
        start_date = (now.replace(day=1) - relativedelta(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(day=1) - timedelta(seconds=1)
        return start_date, end_date

    # Last N months
    import re
    match = re.search(r"last (\d+) months?", text)
    if match:
        n = int(match.group(1))
        end_date = now.replace(day=1) - timedelta(seconds=1)  # end of last month
        start_date = (end_date.replace(day=1) - relativedelta(months=n-1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return start_date, end_date

    # Last week (Monday-Sunday before this week)
    if "last week" in text:
        weekday = now.weekday()  # 0=Monday
        start_of_this_week = now - timedelta(days=weekday)
        start_date = (start_of_this_week - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_of_this_week - timedelta(seconds=1)
        return start_date, end_date

    return None, None



def parse_money(text: str) -> float:
    """
    Convert flexible money inputs like '25k', '25,000', '7.5k' into numeric value.
    """
    text = text.replace(',', '').lower().strip()
    if 'k' in text:
        return float(text.replace('k', '')) * 1000
    return float(text)


# Helper function to detect fixed categories
async def detect_fixed_category(category: str, user_id: str) -> bool:
    category = category.lower()
    fixed_keywords = ["rent", "eb", "electricity", "internet", "wifi", "insurance", "loan"]

    if any(word in category for word in fixed_keywords):
        return True

    # Check if category is recurring in user's past expenses (monthly)
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    past_expenses_cursor = db.expenses.find({
        "user_id": user_id,
        "category": category,
        "date": {"$gte": one_month_ago.isoformat()}
    })
    count = 0
    async for _ in past_expenses_cursor:
        count += 1

    if count >= 1:  # appeared at least once in the last month
        return True

    return False