import re
from fastapi import APIRouter, Header, HTTPException
from bson import ObjectId

from ..db import db
from .auth_routes import verify_token

router = APIRouter(prefix="/expense", tags=["expense"])

@router.post("/set-salary")
async def set_salary(salary_input: str, authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]

    s = salary_input.replace(",", "").lower().strip()
    salary_value = 0.0
    if "k" in s:
        match = re.search(r"(\d+(\.\d+)?)k", s)
        if match:
            salary_value = float(match.group(1)) * 1000
    else:
        salary_value = float(s)

    if salary_value <= 0:
        raise HTTPException(status_code=400, detail="Invalid salary amount")

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"salary": salary_value}},
        upsert=True
    )
    return {"message": f"Salary set to Rs.{salary_value}"}

@router.get("/analytics")
async def expense_analytics(authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]

    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$category",
            "total": {"$sum": "$amount"}
        }}
    ]
    analytics = await db.expenses.aggregate(pipeline).to_list(length=None)
    return {"analytics": analytics}