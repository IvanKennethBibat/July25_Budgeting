import os
import sqlite3
import pytest
from database import init_db, save_budget, get_budgets, DB_PATH

@pytest.fixture(autouse=True)
def setup_teardown():
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()
    yield
    if DB_PATH.exists():
        os.remove(DB_PATH)

def test_database_save_and_load():
    plan = {
        "Debt": 200,
        "Dates": 100,
        "Needs": 525.0,
        "Wants": 315.0,
        "Savings": 960.0
    }
    save_budget("2025-07", 2100, plan)
    records = get_budgets()
    assert len(records) == 1
    assert records[0][1] == "2025-07"
    assert records[0][2] == 2100