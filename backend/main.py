from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import List
from pydantic import BaseModel, Field
from mysql.connector.errors import IntegrityError
import auth
import database

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Expenses(BaseModel):
    amount: float
    category: str
    notes: str

class ExpensesWithDate(Expenses):
    expense_date: date

class DateRange(BaseModel):
    start_date: date
    end_date: date


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    user = auth.verify_token(authorization[7:])
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user


@app.post("/auth/signup")
def signup(credentials: Credentials):
    if not credentials.username.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Username may contain only letters, numbers, and underscores")
    try:
        user = database.create_user(
            credentials.username, auth.hash_password(credentials.password)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username already exists")
    return {"token": auth.create_token(user["id"], user["username"]), "username": user["username"]}


@app.post("/auth/login")
def login(credentials: Credentials):
    user = database.get_user(credentials.username)
    if user is None or not auth.verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": auth.create_token(user["id"], user["username"]), "username": user["username"]}

@app.get("/expenses", response_model=List[ExpensesWithDate])
def get_all_expenses(user=Depends(get_current_user)):
    expenses = database.get_all_expenses(user["user_id"])

    return expenses
    

@app.get("/expenses/{expense_date}", response_model=List[Expenses])
def get_expenses(expense_date: date, user=Depends(get_current_user)):
    expenses = database.get_expense(user["user_id"], expense_date)
     
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expenses], user=Depends(get_current_user)):
    database.delete_expense(user["user_id"], expense_date)

    for expense in expenses:
        database.insert_expense(user["user_id"], expense_date, expense.amount, expense.category, expense.notes)

    return {"message": "Expense Updated successfully"}


@app.post("/analytics")
def get_analytics(date_range: DateRange, user=Depends(get_current_user)):
    data = database.fetch_expense_summary(user["user_id"], date_range.start_date, date_range.end_date)

    if data is None:
        raise Exception("Failed to retrieve the data")

    total = sum([row['total'] for row in data])

    breakdown = {}

    for row in data:
        percentage = (row['total']/total)* 100 if total !=0  else 0
        breakdown[row['category']] = {
             "total": row['total'],
             "percentage": percentage 
        }

    return breakdown 