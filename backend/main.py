from fastapi import FastAPI
from datetime import date
from typing import List
from pydantic import BaseModel
import database

app = FastAPI()


class Expenses(BaseModel):
    amount: float
    category: str
    notes: str

class ExpensesWithDate(Expenses):
    expense_date: date

class DateRange(BaseModel):
    start_date: date
    end_date: date

@app.get("/expenses", response_model=List[ExpensesWithDate])
def get_all_expenses():
    expenses = database.get_all_expenses()

    return expenses
    

@app.get("/expenses/{expense_date}", response_model=List[Expenses])
def get_expenses(expense_date: date):
    expenses = database.get_expense(expense_date)
     
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expenses]):
    database.delete_expense(expense_date)

    for expense in expenses:
        database.insert_expense(expense_date, expense.amount, expense.category, expense.notes)

    return {"message": "Expense Updated successfully"}


@app.post("/analytics")
def get_analytics(date_range: DateRange):
    data = database.fetch_expense_summary(date_range.start_date, date_range.end_date)

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