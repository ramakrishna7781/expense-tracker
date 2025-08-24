from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterBody(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginBody(BaseModel):
    email: EmailStr
    password: str

class ExpenseInput(BaseModel):
    text: str  # like "500 petrol"

class ExpenseDB(BaseModel):
    user_id: str
    amount: float
    category: str
    description: str
    date: Optional[str]  # ISO format
