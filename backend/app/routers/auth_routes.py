from fastapi import APIRouter, HTTPException, Header
from jose import jwt, JWTError, ExpiredSignatureError
import os

from ..models import RegisterBody, LoginBody
from ..db import db
from ..auth import hash_password, verify_password, create_token
from bson import ObjectId

JWT_SECRET = os.getenv("JWT_SECRET")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(body: RegisterBody):
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    _id = ObjectId()
    await db.users.insert_one({
        "_id": _id,
        "name": body.name,
        "email": body.email,
        "password_hash": hash_password(body.password),
    })
    token = create_token({"sub": str(_id)})
    return {"access_token": token}

@router.post("/login")
async def login(body: LoginBody):
    user = await db.users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token({"sub": str(user["_id"])} )
    return {"access_token": token}

def verify_token(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")