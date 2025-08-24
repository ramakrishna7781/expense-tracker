# # app/main.py
# import os
# from dotenv import load_dotenv

# load_dotenv()
# HF_API_KEY = os.getenv("HF_API_KEY")
# MONGO_URL = os.getenv("MONGO_URL")
# DB_NAME = os.getenv("DB_NAME")
# JWT_SECRET = os.getenv("JWT_SECRET")

# from fastapi import FastAPI
# from app.routers import auth_routes, expense_routes, pdf_routes, genai_routes

# app = FastAPI(title="AI Expense Tracker")
# app.include_router(auth_routes.router)
# app.include_router(expense_routes.router)
# app.include_router(pdf_routes.router)
# app.include_router(genai_routes.router)


# app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")

# Import routers
from app.routers import auth_routes, expense_routes, pdf_routes, genai_routes

# Initialize FastAPI app
app = FastAPI(title="AI Expense Tracker")

# Add CORS middleware (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(expense_routes.router)
app.include_router(pdf_routes.router)
app.include_router(genai_routes.router)
