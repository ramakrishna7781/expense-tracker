from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes, command_router, expense_routes, pdf_routes

app = FastAPI(title="AI Expense Tracker")

# Replace with your actual frontend URL for production
origins = [
    "http://localhost:5173",
    "https://your-frontend-url.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(command_router.router)
app.include_router(expense_routes.router)
app.include_router(pdf_routes.router)