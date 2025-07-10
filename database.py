import sqlite3
from pathlib import Path

DB_PATH = Path("storage/budget.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY,
            month TEXT,
            income REAL,
            debt REAL,
            dates REAL,
            needs REAL,
            wants REAL,
            savings REAL
        )
    """)
    conn.commit()
    conn.close()

def save_budget(month, income, plan):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (month, income, debt, dates, needs, wants, savings)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        month,
        income,
        plan['Debt'],
        plan['Dates'],
        plan['Needs'],
        plan['Wants'],
        plan['Savings']
    ))
    conn.commit()
    conn.close()

def get_budgets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows