# from fastapi import APIRouter
# from ..db import db
# from ..utils import generate_pdf
# from datetime import datetime
# import os

# router = APIRouter(prefix="/pdf", tags=["pdf"])

# @router.get("/monthly")
# async def download_monthly_pdf(user_id: str = "dummy_user"):
#     cursor = db.expenses.find({"user_id": user_id})
#     expenses = []
#     async for e in cursor:
#         expenses.append(e)
#     if not expenses:
#         return {"detail": "No expenses found"}

#     filename = f"{user_id}_{datetime.utcnow().strftime('%Y-%m')}.pdf"
#     generate_pdf(user_id, expenses, filename)

#     # Delete old expenses
#     await db.expenses.delete_many({"user_id": user_id})
#     return {"filename": filename, "message": "PDF generated and old data deleted"}


from fastapi import APIRouter
from ..db import db
from ..utils import generate_pdf
from datetime import datetime, timezone
import os

router = APIRouter(prefix="/pdf", tags=["pdf"])

@router.get("/monthly")
async def download_monthly_pdf(user_id: str = "dummy_user"):
    # Fetch all expenses for the user
    cursor = db.expenses.find({"user_id": user_id})
    expenses = []
    async for e in cursor:
        expenses.append(e)

    if not expenses:
        return {"detail": "No expenses found"}

    # Use timezone-aware UTC datetime for filename
    now_utc = datetime.now(timezone.utc)
    filename = f"{user_id}_{now_utc.strftime('%Y-%m')}.pdf"

    # Generate PDF
    generate_pdf(user_id, expenses, filename)

    # Delete old expenses after PDF generation
    await db.expenses.delete_many({"user_id": user_id})

    return {"filename": filename, "message": "PDF generated and old data deleted"}
