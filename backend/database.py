import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Establishing the Connection with DB
def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "expense_manager"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

    if (connection.is_connected):
        print("Connection Established Successfully!")

        cursor = connection.cursor(dictionary=True)
    else:
        raise ConnectionError("Error while connecting to the database!")

    return connection, cursor


# Getting All expenses
def get_all_expenses():
    connection, cursor = get_connection()

    cursor.execute("SELECT * FROM expenses ORDER BY expense_date DESC;")
    values = cursor.fetchall()

    for value in values:
        print(value)

    cursor.close()
    connection.close()

    return values



# Getting expenses by Date
def get_expense(expense_date):
    connection, cursor = get_connection()

    cursor.execute("SELECT * FROM expenses WHERE expense_date=%s", (expense_date,))

    value = cursor.fetchall()

    return value


# For Inserting the values in expenses
def insert_expense(expense_date, amount, category, notes):
    connection, cursor = get_connection()

    cursor.execute("INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)", (expense_date, amount, category, notes))

    connection.commit()

    print("Expense Record Inserted Successfully")


# For Updating an Expense by Date
def update_expense(expense_date):
    connection, cursor = get_connection()

    print(f"Updating expense with date = {expense_date}")
    amount = float(input("Enter new amount: "))
    category = input("Enter new category: ")
    notes = input("Enter new notes: ")

    cursor.execute(
        """
        UPDATE expenses
        SET expense_date = %s,
            amount = %s,
            category = %s,
            notes = %s
        WHERE expense_date = %s
        """,
        (expense_date, amount, category, notes, expense_date)
    )

    connection.commit()

    print("Expense updated successfully!")

    cursor.close()
    connection.close()


# Deleting expense by Date
def delete_expense(expense_date):
    connection, cursor = get_connection()

    cursor.execute(
        "DELETE FROM expenses WHERE expense_date = %s",
        (expense_date,)
    )
    connection.commit()

    print(f"Expense with date {expense_date} deleted successfully.")


# Fetching Expense Summary
def fetch_expense_summary(start_date, end_date):
    connection, cursor = get_connection()   

    cursor.execute("SELECT category, SUM(amount) AS total FROM expenses WHERE expense_date BETWEEN %s AND %s GROUP BY category;", (start_date, end_date))

    values = cursor.fetchall()

    cursor.close()
    connection.close()
    return values
