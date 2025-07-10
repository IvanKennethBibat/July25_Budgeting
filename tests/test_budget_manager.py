import pytest
from budget_manager import BudgetManager

def test_calculate_budget_basic():
    bm = BudgetManager(2000)
    plan = bm.calculate_budget()
    assert plan["Debt"] == 200  # 600 // 3
    assert plan["Dates"] == 100  # 25 * 4
    assert plan["Needs"] == 500.00  # 0.25 * 2000
    assert plan["Wants"] == 300.00  # 0.15 * 2000
    assert plan["Savings"] == 900.00  # 2000 - (200 + 100 + 500 + 300)

def test_calculate_budget_rounding():
    bm = BudgetManager(1234)
    plan = bm.calculate_budget()
    assert plan["Needs"] == round(0.25 * 1234, 2)
    assert plan["Wants"] == round(0.15 * 1234, 2)
    # Check that all values are rounded to 2 decimals except Debt and Dates
    assert isinstance(plan["Needs"], float)
    assert isinstance(plan["Wants"], float)

def test_calculate_budget_zero_income():
    bm = BudgetManager(0)
    plan = bm.calculate_budget()
    assert plan["Needs"] == 0
    assert plan["Wants"] == 0
    assert plan["Savings"] == -300  # 0 - (200 + 100 + 0 + 0)

def test_calculate_budget_high_income():
    bm = BudgetManager(10000)
    plan = bm.calculate_budget()
    assert plan["Debt"] == pytest.approx(200)
    assert plan["Dates"] == pytest.approx(100)
    assert plan["Needs"] == pytest.approx(2500.00)
    assert plan["Wants"] == pytest.approx(1500.00)
    assert plan["Savings"] == pytest.approx(5700.00)

def test_plan_is_dict():
    bm = BudgetManager(5000)
    plan = bm.calculate_budget()
    assert isinstance(plan, dict)
    for key in ["Debt", "Dates", "Needs", "Wants", "Savings"]:
        assert key in plan