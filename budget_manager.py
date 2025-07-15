class BudgetManager:
    def __init__(self, income, expenditure, allocation=None):
        self.income = income
        self.expenditure = expenditure
        self.allocation = allocation or {"Needs": 50, "Wants": 30, "Savings": 20}
        self.plan = {}

    def calculate_budget(self):
        disposable_income = self.income - self.expenditure

        needs = (self.allocation["Needs"] / 100) * disposable_income
        wants = (self.allocation["Wants"] / 100) * disposable_income
        savings = disposable_income - needs - wants

        self.plan = {
            "Needs": round(needs, 2),
            "Wants": round(wants, 2),
            "Savings": round(savings, 2)
        }
        return self.plan
    
    def update_allocation(self, category, value):
        # Calculate current total excluding the modified category
        other_total = 100 - self.allocation[category]
        
        # Calculate scaling factor for other categories
        scale = (100 - value) / other_total if other_total > 0 else 1
        
        # Update all categories proportionally
        for cat in self.allocation:
            if cat != category:
                self.allocation[cat] = round(self.allocation[cat] * scale, 1)
        
        # Update the modified category
        self.allocation[category] = value
        
        # Ensure exact 100% total
        self._normalize_total()

    def _normalize_total(self):
        total = sum(self.allocation.values())
        if total != 100:
            # Distribute rounding difference proportionally
            diff = 100 - total
            largest_cat = max(self.allocation, key=self.allocation.get)
            self.allocation[largest_cat] += diff