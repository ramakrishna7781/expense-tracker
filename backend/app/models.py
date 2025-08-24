from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class RegisterBody(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginBody(BaseModel):
    email: EmailStr
    password: str

# Model for the /command endpoint input
class CommandInput(BaseModel):
    text: str

# New structured model for adding/editing an expense
class ExpenseModel(BaseModel):
    description: str
    amount: float
    category: str
    date: Optional[datetime] = None