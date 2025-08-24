from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests

router = APIRouter(prefix="/genai", tags=["genai"])
HF_API_KEY = os.getenv("HF_API_KEY")
HF_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

class ParseInput(BaseModel):
    text: str

def query_hf(text: str):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"Classify this expense into category and amount: {text}"}
    response = requests.post(HF_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="GenAI API failed")
    return response.json()[0]["generated_text"]

@router.post("/parse")
async def parse_expense(body: ParseInput):
    result = query_hf(body.text)
    # Expected format: "amount: 500, category: Travel, description: petrol"
    return {"parsed": result}
