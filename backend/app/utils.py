import os
from fpdf import FPDF
from datetime import datetime

def generate_pdf(user_id: str, expenses: list, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Expense Report for User: {user_id}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
    pdf.ln(10)

    categories = {}
    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]

    pdf.cell(200, 10, txt="Category-wise summary:", ln=True)
    for cat, amt in categories.items():
        pdf.cell(200, 10, txt=f"{cat}: ₹{amt}", ln=True)

    pdf.output(filename)
