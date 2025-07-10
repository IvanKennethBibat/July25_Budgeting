import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem

from ui_mainwindow import Ui_MainWindow
from budget_manager import BudgetManager
from database import init_db, save_budget, get_budgets
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
    window.btn_view_history.clicked.connect(show_history_window)
    window.show()
    sys.exit(app.exec())

def show_history_window():
    history_data = get_budgets()

    dialog = QDialog()
    dialog.setWindowTitle("Budget History")
    dialog.setFixedSize(500, 400)

    table = QTableWidget()
    table.setColumnCount(7)
    table.setHorizontalHeaderLabels(["ID", "Month", "Income", "Debt", "Dates", "Needs", "Wants", "Savings"])
    table.setRowCount(len(history_data))

    for row_idx, row_data in enumerate(history_data):
        for col_idx, value in enumerate(row_data):
            table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    layout = QVBoxLayout()
    layout.addWidget(table)
    dialog.setLayout(layout)
    dialog.exec()

if __name__ == "__main__":
    main()