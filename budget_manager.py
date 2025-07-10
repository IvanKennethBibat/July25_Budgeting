class BudgetManager:
    def __init__(self, income):
        self.income = income
        self.debt_due = 600
        self.months_left = 3
        self.weekly_dates = 4
        self.plan = {}

    def calculate_budget(self):
        debt_payment = self.debt_due // self.months_left
        date_budget = 25 * self.weekly_dates
        needs = 0.25 * self.income
        wants = 0.15 * self.income
        savings = self.income - (debt_payment + date_budget + needs + wants)

        self.plan = {
            "Debt": debt_payment,
            "Dates": date_budget,
            "Needs": round(needs, 2),
            "Wants": round(wants, 2),
            "Savings": round(savings, 2)
        }
        return self.plan