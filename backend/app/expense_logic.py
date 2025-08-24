from bson import ObjectId
from datetime import datetime, timezone, timedelta
from typing import Optional
from calendar import monthrange

from .db import db
from .models import ExpenseModel

async def add_expense(user_id: str, expense_data: ExpenseModel):
    """Adds a new expense to the database."""
    expense_dict = expense_data.model_dump()
    expense_dict["user_id"] = user_id
    expense_dict["date"] = (expense_data.date or datetime.now(timezone.utc)).isoformat()

    result = await db.expenses.insert_one(expense_dict)
    created_expense = await db.expenses.find_one({"_id": result.inserted_id})
    if created_expense:
        created_expense["_id"] = str(created_expense["_id"])
    
    # Format the response to be more user-friendly in the chat
    return {
        "response": f"✅ Expense Added!\n"
                    f"Description: {created_expense.get('description')}\n"
                    f"Amount: Rs.{created_expense.get('amount'):.2f}\n"
                    f"Category: {created_expense.get('category')}"
    }

async def list_expenses(user_id: str, category: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """Lists expenses from the database with optional filters."""
    query = {"user_id": user_id}

    if category:
        query["category"] = category

    if start_date:
        end_date = end_date or datetime.now(timezone.utc)
        query["date"] = {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}

    expenses_cursor = db.expenses.find(query).sort("date", -1)
    expenses = await expenses_cursor.to_list(length=None)

    if not expenses:
        return {"response": "I couldn't find any expenses matching your criteria."}

    total = sum(exp.get("amount", 0) for exp in expenses)

    response_lines = []
    if category:
        response_lines.append(f"Total spent on {category}: Rs.{total:.2f}")
    else:
        response_lines.append(f"Total spent: Rs.{total:.2f}")

    for exp in expenses:
        date_str = datetime.fromisoformat(exp['date']).strftime('%b %d')
        response_lines.append(f"- {date_str}: {exp['description']} (Rs.{exp['amount']:.2f}, {exp['category']})")

    return {"response": "\n".join(response_lines)}


async def edit_last_expense(user_id: str, new_amount: float, new_description: str):
    """Finds the most recent expense and updates it."""
    last_expense = await db.expenses.find_one({"user_id": user_id}, sort=[("_id", -1)])

    if not last_expense:
        return {"response": "You don't have any expenses to edit."}

    update_data = {"amount": new_amount, "description": new_description}
    await db.expenses.update_one({"_id": last_expense["_id"]}, {"$set": update_data})
    
    return {"response": f"✅ Got it. I've updated your last expense to be '{new_description}' for Rs.{new_amount:.2f}."}

async def analyze_spending_query(user_id: str, query: str, requested_amount: Optional[float] = None):
    """Analyzes a user's spending query and provides a detailed suggestion."""
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user_data or "salary" not in user_data:
        return {"response": "Your salary isn't set. Try 'Set my salary to 50k' first."}

    salary = user_data.get("salary", 0)
    savings_goal = user_data.get("savings_goal", 0)
    
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    _, days_in_month = monthrange(now.year, now.month)
    end_of_month = now.replace(day=days_in_month, hour=23, minute=59, second=59, microsecond=0)

    expenses_cursor = db.expenses.find({"user_id": user_id, "date": {"$gte": start_of_month.isoformat()}})
    total_spent = sum(e.get("amount", 0) for e in await expenses_cursor.to_list(length=None))

    remaining_budget = (salary - savings_goal) - total_spent
    days_remaining = max(1, (end_of_month - now).days + 1)
    safe_daily_spend = remaining_budget / days_remaining

    final_requested_amount = requested_amount or 0.0

    if final_requested_amount == 0:
        return {"response": f"Here's your summary for the month:\n- Total Spent: Rs.{total_spent:,.2f}\n- Remaining Budget: Rs.{remaining_budget:,.2f}\n- Safe daily spend: Rs.{safe_daily_spend:,.2f}"}
    
    if final_requested_amount > remaining_budget:
        return {"response": f"❌ No. Spending Rs.{final_requested_amount:,.2f} would exceed your total remaining budget of Rs.{remaining_budget:,.2f}."}

    if final_requested_amount <= safe_daily_spend:
        return {"response": f"✅ Yes, you can. Spending Rs.{final_requested_amount:,.2f} is within your safe daily budget of Rs.{safe_daily_spend:,.2f}."}
    else:
        return {"response": f"⚠️ You can, but be careful. Spending Rs.{final_requested_amount:,.2f} is more than your safe daily average of Rs.{safe_daily_spend:,.2f}."}