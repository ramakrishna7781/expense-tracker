from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from fpdf import FPDF
from io import BytesIO
from datetime import datetime, timezone

from ..db import db
from .auth_routes import verify_token

router = APIRouter(prefix="/pdf", tags=["pdf"])

def create_pdf_in_memory(user_id: str, expenses: list) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Expense Report", ln=True, align='C')
    # ... (rest of PDF generation logic)
    
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer

@router.get("/monthly")
async def download_monthly_pdf(authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]
    
    cursor = db.expenses.find({"user_id": user_id})
    expenses = await cursor.to_list(length=None)

    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found.")

    pdf_buffer = create_pdf_in_memory(user_id, expenses)
    filename = f"Report_{datetime.now(timezone.utc).strftime('%Y-%m')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )