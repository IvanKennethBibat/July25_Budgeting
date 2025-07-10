import sys
from PyQt6.QtWidgets import QApplication
from ui_mainwindow import Ui_MainWindow
from budget_manager import BudgetManager
from database import init_db, save_budget
init_db()

def main():
    app = QApplication(sys.argv)
    window = Ui_MainWindow()

    def handle_calculate():
        try:
            income = float(window.input_income.text())
            bm = BudgetManager(income)
            plan = bm.calculate_budget()

            # Save to SQLite
            from datetime import datetime
            month = datetime.now().strftime("%Y-%m")
            save_budget(month, income, plan)

            summary = "\n".join([f"{k}: €{v}" for k, v in plan.items()])
            window.result_label.setText("Saved!\n" + summary)

        except ValueError:
            window.result_label.setText("Please enter a valid number.")


    window.btn_calculate.clicked.connect(handle_calculate)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()