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
        port=int(os.getenv("DB_PORT", "3306")),
        autocommit=True,
        ssl_disabled=False if os.getenv("DB_SSL_DISABLED", "false").lower() == "false" else True
    )

    if connection.is_connected():
        print("Connection Established Successfully!")
        cursor = connection.cursor(dictionary=True)
    else:
        raise ConnectionError("Error while connecting to the database!")

    return connection, cursor


def initialize_database():
    connection, cursor = get_connection()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NULL
        )
        """
    )
    cursor.execute(
        """
        SELECT COUNT(*) AS column_count
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'users'
          AND column_name = 'password_hash'
        """
    )
    if cursor.fetchone()["column_count"] == 0:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            expense_date DATE NOT NULL,
            amount FLOAT NOT NULL,
            category VARCHAR(50) NOT NULL,
            notes TEXT,
            INDEX idx_user_date (user_id, expense_date)
        )
        """
    )

    cursor.execute(
        """
        SELECT COUNT(*) AS column_count
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'expenses'
          AND column_name = 'user_id'
        """
    )
    if cursor.fetchone()["column_count"] == 0:
        cursor.execute("ALTER TABLE expenses ADD COLUMN user_id INT NULL")

    cursor.execute("INSERT IGNORE INTO users (username, password_hash) VALUES ('default', NULL)")
    cursor.execute(
        "UPDATE expenses SET user_id = (SELECT id FROM users WHERE username = 'default') WHERE user_id IS NULL"
    )

    cursor.close()
    connection.close()


def create_user(username, password_hash):
    connection, cursor = get_connection()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, password_hash),
    )
    user_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return {"id": user_id, "username": username}


def get_user(username):
    connection, cursor = get_connection()
    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = %s",
        (username,),
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user


# Getting All expenses
def get_all_expenses(user_id):
    connection, cursor = get_connection()

    cursor.execute("SELECT expense_date, amount, category, notes FROM expenses WHERE user_id = %s ORDER BY expense_date DESC", (user_id,))
    values = cursor.fetchall()

    for value in values:
        print(value)

    cursor.close()
    connection.close()

    return values



# Getting expenses by Date
def get_expense(user_id, expense_date):
    connection, cursor = get_connection()

    cursor.execute("SELECT amount, category, notes FROM expenses WHERE user_id = %s AND expense_date = %s", (user_id, expense_date))

    value = cursor.fetchall()

    return value


# For Inserting the values in expenses
def insert_expense(user_id, expense_date, amount, category, notes):
    connection, cursor = get_connection()

    cursor.execute("INSERT INTO expenses (user_id, expense_date, amount, category, notes) VALUES (%s, %s, %s, %s, %s)", (user_id, expense_date, amount, category, notes))

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
def delete_expense(user_id, expense_date):
    connection, cursor = get_connection()

    cursor.execute(
        "DELETE FROM expenses WHERE user_id = %s AND expense_date = %s",
        (user_id, expense_date)
    )
    connection.commit()

    print(f"Expense with date {expense_date} deleted successfully.")


# Fetching Expense Summary
def fetch_expense_summary(user_id, start_date, end_date):
    connection, cursor = get_connection()   

    cursor.execute("SELECT category, SUM(amount) AS total FROM expenses WHERE user_id = %s AND expense_date BETWEEN %s AND %s GROUP BY category", (user_id, start_date, end_date))

    values = cursor.fetchall()

    cursor.close()
    connection.close()
    return values
