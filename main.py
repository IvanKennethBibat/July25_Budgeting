import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QApplication, 
    QDialog, QButtonGroup, QSizePolicy, 

)
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
import datetime
from PyQt6.QtGui import QIcon, QFontDatabase, QFont, QDoubleValidator, QColor
from layout_colorwidget import Color  # Assuming this is the correct import path
from budget_manager import BudgetManager
from allocation_widget import AllocationWidget
from database import init_db, save_budget, get_budgets
init_db()

class BudgetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" ")
        self.setWindowIcon(QIcon("assets/heart_moneybag_10072025.png")) 
        self.setFixedSize(1600, 800)

        self.budget_manager = BudgetManager(0, 0)

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

        self.btn_calculate.clicked.connect(self.handle_calculate)
        self.nav_buttons.idClicked.connect(self.handle_nav_click)

    def build_budget_page(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20) 

        layout.addWidget(QLabel("<b>Income & Expenses</b>"))

        # Input fields
        self.input_income = QLineEdit()
        self.input_income.setPlaceholderText("Enter Monthly Income")
        self.input_income.setValidator(QDoubleValidator(0, 1000000, 2, self)) 

        self.input_expenditure = QLineEdit()
        self.input_expenditure.setPlaceholderText("Enter Monthly Expenditure")
        self.input_expenditure.setValidator(QDoubleValidator(0, 1000000, 2, self))
        
        # Calculate button
        self.btn_calculate = QPushButton("Calculate Budget")
        
        # Result display
        self.result_label = QLabel("Results will appear here")
        self.result_label.setWordWrap(True)

        layout.addWidget(QLabel("<b>Budget Allocation</b>"))
        # Allocation Widget - This handles the spinboxes/progress bars
        self.allocation_widget = AllocationWidget(
            initial_allocation={"Needs": 50, "Wants": 30, "Savings": 20},
            parent=self  # Important for accessing parent methods
        )

        # Chart Setup
        self.series = QPieSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Budget Allocation")
        self.chart.legend().setVisible(True)
        self.chart_view = QChartView(self.chart)
        
        # Add widgets to layout in logical order
        layout.addWidget(self.input_income)
        layout.addWidget(self.input_expenditure)
        layout.addWidget(self.allocation_widget)  # Allocation comes after inputs
        layout.addWidget(self.chart_view)          # Chart below allocation controls
        layout.addWidget(self.btn_calculate)
        layout.addWidget(self.result_label)

        widget = QWidget()
        widget.setLayout(layout)
        
        # Initialize pie chart with starting values
        self.update_pie_chart()
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

    def handle_calculate(self):
        try:
            income = float(self.input_income.text())
            expenditure = float(self.input_expenditure.text())

            # Update manager with current allocation
            self.budget_manager.income = income
            self.budget_manager.expenditure = expenditure
            self.budget_manager.allocation = self.allocation_widget.get_allocation()
            
            plan = self.budget_manager.calculate_budget()

            # Save to database
            month = datetime.now().strftime("%Y-%m")
            save_budget(month, income, plan)

            # Update results
            summary = "\n".join([f"{k}: €{v}" for k, v in plan.items()])
            self.result_label.setText("Saved!\n" + summary)

        except ValueError:
            self.result_label.setText("Please enter valid numbers")

    def handle_nav_click(self, index):
        """Handle navigation with page-specific logic"""
        self.stacked.setCurrentIndex(index)
        self.nav_buttons.button(index).setChecked(True)
        
        # Add page-specific initialization
        if index == 4:  # History page index
            self.update_history_table()

    def update_history_table(self):
        """Populate history table (Moved from main)"""
        self.history_table.clearContents()
        history_data = get_budgets()
        self.history_table.setRowCount(len(history_data))

        for row_idx, row_data in enumerate(history_data):
            for col_idx, value in enumerate(row_data):
                self.history_table.setItem(
                    row_idx, 
                    col_idx, 
                    QTableWidgetItem(str(value)))
    
    def update_pie_chart(self):
        """Update pie chart with current allocation percentages"""
        self.series.clear()
        
        # Get current allocation from budget manager
        allocation = self.budget_manager.allocation
        
        # Add slices with colors
        needs_slice = self.series.append(f"Needs ({allocation['Needs']}%)", allocation['Needs'])
        needs_slice.setColor(QColor("#4e79a7"))  # Blue
        
        wants_slice = self.series.append(f"Wants ({allocation['Wants']}%)", allocation['Wants'])
        wants_slice.setColor(QColor("#f28e2c"))  # Orange
        
        savings_slice = self.series.append(f"Savings ({allocation['Savings']}%)", allocation['Savings'])
        savings_slice.setColor(QColor("#59a14f"))  # Green
        
        # Optional: Add labels to slices
        for slice in self.series.slices():
            slice.setLabelVisible(True)
            slice.setLabelPosition(QPieSlice.LabelPosition.Outside)

def main():
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont("assets/fonts/Inter_28pt-Regular.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Inter_28pt-SemiBold.ttf")
    app.setFont(QFont("Inter", 18))  # Set default font to Inter Regular

    window = BudgetWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

