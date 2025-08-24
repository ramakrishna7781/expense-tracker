from fastapi import APIRouter, Header, HTTPException
from ..models import ExpenseInput
from ..db import db
from datetime import datetime, timedelta, timezone
from ..hf_classifier import classify_expense, parse_query, extract_amount, parse_relative_date_calendar, parse_money, detect_fixed_category
from .auth_routes import verify_token  # JWT verification
from bson import ObjectId

from fastapi.responses import StreamingResponse
from io import BytesIO
from fpdf import FPDF

import re

router = APIRouter(prefix="/expense", tags=["expense"])

# @router.post("/add")
# async def add_expense(body: ExpenseInput, authorization: str = Header(...)):
#     # Extract user_id from JWT
#     user = verify_token(authorization)
#     user_id = user["id"]

#     # Classify the expense using Hugging Face
#     category = classify_expense(body.text)

#     # Extract the amount using HF
#     amount = extract_amount(body.text)

#     exp = {
#         "user_id": user_id,
#         "date": datetime.utcnow().isoformat(),
#         "description": body.text,
#         "category": category,
#         "amount": amount
#     }

#     inserted = await db.expenses.insert_one(exp)
#     exp["_id"] = str(inserted.inserted_id)  # Return ObjectId as string

#     return {"status": "success", "expense": exp}




@router.post("/add")
async def add_expense(body: ExpenseInput, authorization: str = Header(...)):
    # Extract user_id from JWT
    user = verify_token(authorization)
    user_id = user["id"]

    # Classify the expense using Hugging Face
    category = classify_expense(body.text)

    # Extract the amount using HF
    amount = extract_amount(body.text)

    # Determine if expense is fixed
    is_fixed = getattr(body, "is_fixed", None)
    if is_fixed is None:
        is_fixed = await detect_fixed_category(category, user_id)

    exp = {
    "user_id": user_id,
    "date": datetime.now(timezone.utc).isoformat(),  # timezone-aware UTC
    "description": body.text,
    "category": category,
    "amount": amount,
    "is_fixed": is_fixed
}

    inserted = await db.expenses.insert_one(exp)
    exp["_id"] = str(inserted.inserted_id)  # Return ObjectId as string

    return {"status": "success", "expense": exp}



@router.get("/list")
async def list_expenses(query: str = "", authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]

    parsed = parse_query(query)
    categories = parsed["categories"]

    # Check if query has relative date phrases
    start_date, end_date = parse_relative_date_calendar(query)

    mongo_query = {"user_id": user_id}

    # Category filter
    if categories:
        mongo_query["category"] = {"$in": categories}

    # Date filter if detected
    if start_date or end_date:
        mongo_query["date"] = {}
        if start_date:
            mongo_query["date"]["$gte"] = start_date.isoformat()
        if end_date:
            mongo_query["date"]["$lte"] = end_date.isoformat()

    expenses = []
    cursor = db.expenses.find(mongo_query)
    async for e in cursor:
        e["_id"] = str(e["_id"])
        expenses.append(e)

    # Summary
    summary = {}
    for e in expenses:
        cat = e["category"]
        summary[cat] = summary.get(cat, 0) + float(e.get("amount", 0))

    if not expenses:
        return {"total_expenses": 0, "expenses": [], "message": "No expenses found for this query 😅"}

    return {"total_expenses": len(expenses), "summary": summary, "expenses": expenses}



@router.put("/edit/{expense_id}")
async def edit_expense(expense_id: str, body: dict, authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]

    expense = await db.expenses.find_one({"_id": ObjectId(expense_id), "user_id": user_id})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_fields = {}
    for field in ["description", "amount", "category"]:
        if field in body:
            update_fields[field] = body[field]

    if update_fields:
        await db.expenses.update_one({"_id": ObjectId(expense_id)}, {"$set": update_fields})

    updated_expense = await db.expenses.find_one({"_id": ObjectId(expense_id)})
    updated_expense["_id"] = str(updated_expense["_id"])
    return {"status": "success", "expense": updated_expense}


@router.delete("/delete/{expense_id}")
async def delete_expense(expense_id: str, authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]

    result = await db.expenses.delete_one({"_id": ObjectId(expense_id), "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"status": "success", "message": "Expense deleted"}



@router.get("/analytics")
async def expense_analytics(authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]

    # Example aggregation: total spent per category
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$category",
            "total": {"$sum": {"$toDouble": "$amount"}}
        }}
    ]

    analytics = await db.expenses.aggregate(pipeline).to_list(length=None)

    # Convert _id to string for JSON serialization
    for item in analytics:
        item["_id"] = str(item["_id"])

    return {
        "analytics": analytics,
        "message": "Analytics fetched successfully 📊"
    }




@router.get("/download/pdf")
async def download_pdf(authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]

    # Get last month's range
    today = datetime.today()
    first_day_this_month = datetime(today.year, today.month, 1)
    last_month_last_day = first_day_this_month - timedelta(days=1)
    last_month_first_day = datetime(last_month_last_day.year, last_month_last_day.month, 1)

    # Fetch only last month's expenses
    expenses = []
    cursor = db.expenses.find({
        "user_id": user_id,
        "date": {"$gte": last_month_first_day, "$lte": last_month_last_day}
    })
    async for e in cursor:
        expenses.append(e)

    # Group by category and sum amounts
    summary = {}
    for e in expenses:
        category = e.get("category", "Other")
        summary[category] = summary.get(category, 0) + e.get("amount", 0)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Expense Summary - {last_month_first_day.strftime('%B %Y')}", ln=True, align="C")
    pdf.ln(10)

    if not summary:
        # No expenses
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "No spendings in the last month.", ln=True, align="C")
        pdf.cell(0, 10, "You can only download the previous month's statement.", ln=True, align="C")
        pdf.cell(0, 10, "This month's spends can be downloaded on the 1st of next month.", ln=True, align="C")
        pdf.ln(10)  # add some space before closing
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Thank You", ln=True, align="C")
    else:
        # Table header
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(80, 10, "Category", border=1)
        pdf.cell(40, 10, "Total Amount", border=1, ln=True)

        # Table content
        pdf.set_font("Arial", '', 12)
        for category, total in summary.items():
            pdf.cell(80, 10, category, border=1)
            pdf.cell(40, 10, f"Rs.{total}", border=1, ln=True)

    # Output PDF to BytesIO
    pdf_bytes = pdf.output(dest='S').encode('latin1', 'replace')
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=expenses_{last_month_first_day.strftime('%b_%Y')}.pdf"}
    )



@router.post("/set-salary")
async def set_salary(salary_input: str, authorization: str = Header(...)):
    """
    Set the user's monthly salary. Accepts numbers like 25000, 25k, 25,000.
    """
    user = verify_token(authorization)
    user_id = user["id"]

    # Parse salary into a number
    s = salary_input.replace(",", "").lower().strip()
    if "k" in s:
        salary_value = float(s.replace("k", "")) * 1000
    else:
        salary_value = float(s)

    # Save to DB
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"salary": salary_value}},
        upsert=True
    )

    return {"message": f"Salary set to Rs.{salary_value}"}


def contains_money_or_budget_keywords(query: str) -> bool:
    keywords = [
        "spend", "spent", "budget", "salary", "income", "expense", "savings",
        "save", "cost", "price", "amount", "money", "rupee", "rs", "₹"
    ]
    if re.search(r"\d+", query):  # any number mentioned
        return True
    return any(word in query.lower() for word in keywords)



# @router.get("/suggest-spending")
# async def suggest_spending(authorization: str = Header(...), query: str = ""):
#     user = verify_token(authorization)
#     user_id = user["id"]

#     # 1️⃣ Handle random greetings or non-actionable queries
#     if not contains_money_or_budget_keywords(query):
#         return {
#             "response": "👋 Hey! I can help with budget, expenses, or spending suggestions. "
#                         "Try: 'Set my salary 25k', 'Can I spend 200 more today?', or "
#                         "'Categorize my remaining budget into food, petrol, other needs.'"
#         }

#     # 2️⃣ Load user data
#     user_data = await db.users.find_one({"_id": ObjectId(user_id)})
#     if not user_data or "salary" not in user_data:
#         return {"error": "Salary not set. Please set your salary first."}

#     salary = user_data["salary"]
#     savings_goal = user_data.get("savings_goal", 0)

#     # 3️⃣ Parse time frame from query
#     start_date, end_date = parse_relative_date_calendar(query)
#     if not start_date:
#         now = datetime.utcnow()
#         start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         end_date = now.replace(day=now.day, hour=23, minute=59, second=59, microsecond=0)

#     # 4️⃣ Fetch expenses in that time frame
#     expenses_cursor = db.expenses.find({
#         "user_id": user_id,
#         "date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
#     })
#     expenses = []
#     async for e in expenses_cursor:
#         expenses.append(e)

#     # 5️⃣ Group by category
#     summary = {}
#     total_spent = 0
#     for e in expenses:
#         cat = e.get("category", "Other")
#         amount = e.get("amount", 0)
#         total_spent += amount
#         summary[cat] = summary.get(cat, 0) + amount

#     # 6️⃣ Compute remaining budget
#     remaining_budget = salary - total_spent - savings_goal

#     # 7️⃣ Detect requested extra spend or allocation
#     match = re.search(r'(\d+(?:[\.,]?\d+)?\s*[kK]?)', query)
#     requested_amount = parse_money(match.group(0)) if match else 0

#     allocation_keywords = re.findall(r'food|petrol|needs|other|outing|rent', query.lower())
#     is_allocation_query = len(allocation_keywords) > 1

#     # 8️⃣ Calculate days remaining
#     today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
#     end_date_adjusted = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
#     days_remaining = max(1, (end_date_adjusted - today).days + 1)
#     safe_daily_budget = round(max(0, remaining_budget / days_remaining), 2)

#     message = ""

#     # 9️⃣ Allocation query logic
#     per_category_safe_daily_budget = {}
#     if is_allocation_query and remaining_budget > 0:
#         categories = list(set(allocation_keywords))
#         # Equal split among requested categories
#         per_category_amount = round(remaining_budget / len(categories), 2)
#         category_summary_alloc = {cat.capitalize(): per_category_amount for cat in categories}
#         per_category_safe_daily_budget = {cat: round(per_category_amount / days_remaining, 2) for cat in categories}
#         message = (f"Your remaining budget of Rs.{remaining_budget} has been allocated into "
#                    f"{', '.join(category_summary_alloc.keys())} for the rest of the period.")
#         summary.update(category_summary_alloc)

#     #  🔟 Normal spending request logic
#     elif requested_amount > 0:
#         if requested_amount <= remaining_budget:
#             message = (f"✅ You can spend Rs.{requested_amount} more now. "
#                        f"This leaves around Rs.{int(safe_daily_budget - requested_amount)} per day for remaining days.")
#         else:
#             adjustable = sum(v for k, v in summary.items() if k not in ["Needs", "Rent", "Food"])
#             if requested_amount <= remaining_budget + adjustable:
#                 message = (f"⚠️ You can spend Rs.{requested_amount} if you reduce other non-essential spends "
#                            f"(like Shopping).")
#             else:
#                 message = (f"❌ You cannot spend Rs.{requested_amount}. Only Rs.{int(remaining_budget)} left "
#                            f"considering your savings target.")
#     else:
#         message = "Here's your budget summary for the period."

#     return {
#         "salary": salary,
#         "savings_goal": savings_goal,
#         "total_spent": total_spent,
#         "remaining_budget": remaining_budget,
#         "category_summary": summary,
#         "per_category_safe_daily_budget": per_category_safe_daily_budget,
#         "message": message
#     }


@router.get("/suggest-spending")
async def suggest_spending(authorization: str = Header(...), query: str = ""):
    user = verify_token(authorization)
    user_id = user["id"]

    # 1️⃣ Handle random greetings or non-actionable queries
    if not contains_money_or_budget_keywords(query):
        return {
            "response": "👋 Hey! I can help with budget, expenses, or spending suggestions. "
                        "Try: 'Set my salary 25k', 'Can I spend 200 more today?', or "
                        "'Categorize my remaining budget into food, petrol, other needs.'"
        }

    # 2️⃣ Load user data
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user_data or "salary" not in user_data:
        return {"error": "Salary not set. Please set your salary first."}

    salary = user_data["salary"]
    savings_goal = user_data.get("savings_goal", 0)

    # 3️⃣ Parse time frame from query
    start_date, end_date = parse_relative_date_calendar(query)
    if not start_date:
        # FIX 1: Use timezone-aware datetime to prevent TypeError
        now = datetime.now(timezone.utc)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # FIX 2: Calculate the ACTUAL end of the current month for accurate budgeting
        next_month = now.replace(day=28) + timedelta(days=4)
        end_of_month = next_month - timedelta(days=next_month.day)
        end_date = end_of_month.replace(hour=23, minute=59, second=59, microsecond=0)

    # 4️⃣ Fetch expenses in that time frame
    expenses_cursor = db.expenses.find({
        "user_id": user_id,
        "date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
    })
    expenses = []
    async for e in expenses_cursor:
        expenses.append(e)

    # 5️⃣ Group by category
    summary = {}
    total_spent = 0
    for e in expenses:
        cat = e.get("category", "Other")
        amount = e.get("amount", 0)
        total_spent += amount
        summary[cat] = summary.get(cat, 0) + amount

    # 6️⃣ Compute remaining budget
    remaining_budget = salary - total_spent - savings_goal

    # 7️⃣ Detect requested extra spend or allocation
    match = re.search(r'(\d+(?:[\.,]?\d+)?\s*[kK]?)', query)
    requested_amount = parse_money(match.group(0)) if match else 0

    allocation_keywords = re.findall(r'food|petrol|needs|other|outing|rent', query.lower())
    is_allocation_query = len(allocation_keywords) > 1

    # 8️⃣ Calculate days remaining (This will now work correctly)
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date_adjusted = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
    days_remaining = max(1, (end_date_adjusted - today).days + 1)
    safe_daily_budget = round(max(0, remaining_budget / days_remaining), 2)

    message = ""

    # 9️⃣ Allocation query logic
    per_category_safe_daily_budget = {}
    if is_allocation_query and remaining_budget > 0:
        categories = list(set(allocation_keywords))
        per_category_amount = round(remaining_budget / len(categories), 2)
        category_summary_alloc = {cat.capitalize(): per_category_amount for cat in categories}
        per_category_safe_daily_budget = {cat: round(per_category_amount / days_remaining, 2) for cat in categories}
        message = (f"Your remaining budget of Rs.{remaining_budget} has been allocated into "
                   f"{', '.join(category_summary_alloc.keys())} for the rest of the period.")
        summary.update(category_summary_alloc)

    #  🔟 Normal spending request logic
    elif requested_amount > 0:
        if requested_amount <= remaining_budget:
            message = (f"✅ You can spend Rs.{requested_amount} more now. "
                       f"This leaves around Rs.{int(safe_daily_budget - requested_amount)} per day for remaining days.")
        else:
            adjustable = sum(v for k, v in summary.items() if k not in ["Needs", "Rent", "Food"])
            if requested_amount <= remaining_budget + adjustable:
                message = (f"⚠️ You can spend Rs.{requested_amount} if you reduce other non-essential spends "
                           f"(like Shopping).")
            else:
                message = (f"❌ You cannot spend Rs.{requested_amount}. Only Rs.{int(remaining_budget)} left "
                           f"considering your savings target.")
    else:
        message = "Here's your budget summary for the period."

    return {
        "salary": salary,
        "savings_goal": savings_goal,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "category_summary": summary,
        "per_category_safe_daily_budget": per_category_safe_daily_budget,
        "message": message
    }