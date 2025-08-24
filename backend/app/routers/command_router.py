import os
from fastapi import APIRouter, Header, HTTPException
import google.generativeai as genai
from datetime import datetime

from ..models import CommandInput, ExpenseModel
from .auth_routes import verify_token
from .. import expense_logic

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ RESTORED detailed descriptions for all parameters. This is the main fix.
tools = [
    {
        "name": "add_expense",
        "description": "Record a new expense the user has made.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "amount": {"type": "NUMBER", "description": "The amount of money spent, extracted from the text (e.g., '1.5k' becomes 1500)."},
                "category": {
                    "type": "STRING",
                    "description": "The category of the expense based on the description.",
                    "enum": ["Food", "Petrol", "Rent", "Electricity", "Outing", "Movies", "Shopping", "General"]
                },
                "description": {"type": "STRING", "description": "A brief description of the expense, taken from the user's text."},
                "date": {"type": "STRING", "description": "The date of the expense in YYYY-MM-DD format. Infer this from the text (e.g., 'yesterday', 'today')."}
            },
            "required": ["amount", "category", "description"]
        }
    },
    {
        "name": "edit_expense",
        "description": "Correct or update the user's most recently added expense.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "new_amount": {"type": "NUMBER", "description": "The corrected amount of the expense."},
                "new_description": {"type": "STRING", "description": "The corrected full description of the expense."}
            },
            "required": ["new_amount", "new_description"]
        }
    },
    {
        "name": "list_expenses",
        "description": "List, show, or retrieve past expenses based on criteria.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {"type": "STRING", "description": "The category to filter expenses by (e.g., 'Food')."},
                "start_date": {"type": "STRING", "description": "The start date for the filter, in YYYY-MM-DD format."},
                "end_date": {"type": "STRING", "description": "The end date for the filter, in YYYY-MM-DD format."}
            }
        }
    },
    {
        "name": "suggest_spending",
        "description": "Answer a general financial question or provide a budget suggestion.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "The user's full, original question."},
                "amount": {"type": "NUMBER", "description": "The specific amount of money being asked about."}
            },
            "required": ["query"]
        }
    }
]

model = genai.GenerativeModel('gemini-1.5-flash-latest', tools=tools)
router = APIRouter(prefix="/command", tags=["command"])

@router.post("/")
async def handle_command(body: CommandInput, authorization: str = Header(...)):
    user = verify_token(authorization)
    user_id = user["id"]
    try:
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(f"Today's date is {datetime.now().strftime('%Y-%m-%d')}. User's request: {body.text}")
        
        if not response.candidates[0].content.parts or not hasattr(response.candidates[0].content.parts[0], 'function_call'):
            return {"response": response.text}

        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        args = function_call.args or {}

        if function_name == "add_expense":
            expense_data = ExpenseModel(
                description=args.get('description', body.text),
                amount=float(args.get('amount', 0)),
                category=args.get('category', 'General'),
                date=datetime.fromisoformat(args.get('date')) if args.get('date') else None
            )
            return await expense_logic.add_expense(user_id, expense_data)

        elif function_name == "edit_expense":
            return await expense_logic.edit_last_expense(user_id, args.get("new_amount"), args.get("new_description"))
        
        elif function_name == "list_expenses":
            start_date = datetime.fromisoformat(args.get('start_date')) if args.get('start_date') else None
            end_date = datetime.fromisoformat(args.get('end_date')) if args.get('end_date') else None
            return await expense_logic.list_expenses(user_id, args.get('category'), start_date, end_date)

        elif function_name == "suggest_spending":
            return await expense_logic.analyze_spending_query(user_id, args.get('query'), args.get('amount'))
        
        else:
            raise HTTPException(status_code=400, detail="Could not understand the command.")
    except Exception as e:
        print(f"Error processing command: {e}")
        return {"response": "Sorry, I ran into a problem. Please try again."}