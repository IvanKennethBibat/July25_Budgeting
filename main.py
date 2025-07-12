import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QApplication, 
    QDialog, QButtonGroup, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFontDatabase, QFont
from layout_colorwidget import Color  # Assuming this is the correct import path
from budget_manager import BudgetManager
from database import init_db, save_budget, get_budgets
init_db()


class BudgetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" ")
        self.setWindowIcon(QIcon("assets/heart_moneybag_10072025.png")) 
        self.setFixedSize(1600, 800)

        # === Create Nav Buttons ===
        self.btn_nav_dashboard = QPushButton("Dashboard")
        self.btn_nav_budget = QPushButton("Budget")
        self.btn_nav_transactions = QPushButton("Transactions")
        self.btn_nav_analytics = QPushButton("Analytics")
        self.btn_nav_history = QPushButton("History")

                        # Button group for tab behavior
        self.nav_buttons = QButtonGroup()
        self.nav_buttons.setExclusive(True)

        self.nav_buttons.addButton(self.btn_nav_dashboard, 0)
        self.nav_buttons.addButton(self.btn_nav_budget, 1)
        self.nav_buttons.addButton(self.btn_nav_transactions, 2)
        self.nav_buttons.addButton(self.btn_nav_analytics, 3)
        self.nav_buttons.addButton(self.btn_nav_history, 4)

        nav_font = QFont()
        nav_font.setFamilies(["Inter SemiBold", "Inter", "Segoe UI Semibold", "Arial"]) 
        nav_font.setWeight(QFont.Weight.DemiBold)
        nav_font.setPixelSize(20)

        for btn in self.nav_buttons.buttons():
            btn.setFont(nav_font) 
            btn.setCheckable(True)
            btn.setMinimumHeight(50)  # Make buttons full height of navbar
            btn.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    border: none;
                    padding: 10px;
                    color: #c3bdbd;
                    background-color: transparent;

                    border-bottom: 4px solid transparent;
                }
                QPushButton:hover {

                }
                QPushButton:checked {
                    border-bottom: 4px solid #0078d4;  /* Blue highlight */
                }
            """)
        
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)


        # Add buttons with equal stretch
        for btn in self.nav_buttons.buttons():
            nav_layout.addWidget(btn)
            nav_layout.setStretchFactor(btn, 1)

        
        nav_layout.addWidget(self.btn_nav_dashboard)
        nav_layout.addWidget(self.btn_nav_budget)
        nav_layout.addWidget(self.btn_nav_transactions)
        nav_layout.addWidget(self.btn_nav_analytics)
        nav_layout.addWidget(self.btn_nav_history)


        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        nav_widget.setFixedHeight(60)  # Static navbar height

        self.nav_buttons.idClicked.connect(self.handle_nav_click)
        # === Set up the Stacked pages ===
        self.stacked = QStackedWidget()
        self.page_dashboard = Color("#000000")  # Placeholder for dashboard page
        self.page_budget = self.build_budget_page()
        self.page_transactions = Color("#000000")  # Placeholder for page_transactions page
        self.page_analytics = Color("#000000")  # Placeholder for page_analytics page
        self.page_history = self.build_history_page()

        self.stacked.addWidget(self.page_dashboard)  # index 0
        self.stacked.addWidget(self.page_budget)     # index 1
        self.stacked.addWidget(self.page_transactions)  # index 2
        self.stacked.addWidget(self.page_analytics)  # index 3
        self.stacked.addWidget(self.page_history)  # index 4

        # === Main Layout ===
        main_layout = QVBoxLayout()
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(self.stacked)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def handle_nav_click(self, index):
        """Handle navigation button clicks to switch pages."""
        self.stacked.setCurrentIndex(index)
        self.nav_buttons.button(index).setChecked(True)

    def build_budget_page(self):
        layout = QVBoxLayout()

        self.input_income = QLineEdit()
        self.input_income.setPlaceholderText("Enter Income")

        self.btn_calculate = QPushButton("Calculate Budget")

        self.result_label = QLabel("Results will appear here")
        self.result_label.setWordWrap(True)

        layout.addWidget(self.input_income)
        layout.addWidget(self.btn_calculate)
        layout.addWidget(self.result_label)
        
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def build_history_page(self):
            layout = QVBoxLayout()

            self.history_table = QTableWidget()
            self.history_table.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )   
            self.history_table.setColumnCount(7)
            self.history_table.setHorizontalHeaderLabels(["ID", "Month", "Income", "Debt", "Dates", "Needs", "Wants", "Savings"])

            self.btn_back = QPushButton("Back to Home")
            layout.addWidget(self.history_table)

            layout.addWidget(self.history_table)
            widget = QWidget()
            widget.setLayout(layout)

            return widget

def main():
    app = QApplication(sys.argv)
    window = BudgetWindow()

    font_id = QFontDatabase.addApplicationFont("assets/fonts/Inter_28pt-Regular.ttf")
    font_id_semibold = QFontDatabase.addApplicationFont("assets/fonts/Inter_28pt-SemiBold.ttf")
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    font_family_semibold = QFontDatabase.applicationFontFamilies(font_id_semibold)[0]

    app.setFont(QFont(font_family, 18))  # Set default font to Inter Regular


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

    def show_history():
        """Fetch and display budget history in the history table."""
        # Clear the table before populating it, to avoid errors
        window.history_table.clearContents()

        # Fetch history data from the database
        history_data = get_budgets()
        window.history_table.setRowCount(len(history_data))

        for row_idx, row_data in enumerate(history_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                window.history_table.setItem(row_idx, col_idx, item)

        window.stacked.setCurrentIndex(1)

    # Hook up navigation buttons
    window.btn_nav_budget.clicked.connect(lambda: window.stacked.setCurrentIndex(0))
    window.btn_nav_history.clicked.connect(lambda: (show_history(), window.stacked.setCurrentIndex(1)))

    # Hooked up core logic
    window.btn_calculate.clicked.connect(handle_calculate)
    # window.btn_view_history.clicked.connect(show_history)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

