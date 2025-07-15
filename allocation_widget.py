from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt

class AllocationWidget(QWidget):
    def __init__(self, initial_allocation, parent=None):
        super().__init__(parent)
        self.allocation = initial_allocation
        self.spinboxes = {}
        
        layout = QVBoxLayout()
        
        # Create UI elements for each category
        for category, value in initial_allocation.items():
            cat_layout = QHBoxLayout()
            
            label = QLabel(f"{category}:")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(80)
            
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setValue(value)
            spinbox.setSingleStep(0.5)
            spinbox.setSuffix("%")
            spinbox.valueChanged.connect(
                lambda val, cat=category: self._handle_value_change(cat, val)
            )
            
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(int(value))
            progress.setTextVisible(False)
            
            cat_layout.addWidget(label)
            cat_layout.addWidget(spinbox)
            cat_layout.addWidget(progress)
            layout.addLayout(cat_layout)
            
            self.spinboxes[category] = (spinbox, progress)
        
        self.setLayout(layout)
    
    def _handle_value_change(self, category, value):
        """Handle spinbox changes while maintaining 100% total"""
        # Block signals during updates to prevent recursion
        for spinbox, _ in self.spinboxes.values():
            spinbox.blockSignals(True)
        
        # Update allocation model
        self.parent().budget_manager.update_allocation(category, value)
        
        # Update UI with normalized values
        for cat, (spinbox, progress) in self.spinboxes.items():
            new_value = self.parent().budget_manager.allocation[cat]
            if spinbox.value() != new_value:
                spinbox.setValue(new_value)
            progress.setValue(int(new_value))
        
        # Update pie chart
        self.parent().update_pie_chart()
        
        # Re-enable signals
        for spinbox, _ in self.spinboxes.values():
            spinbox.blockSignals(False)
    
    def get_allocation(self):
        return self.parent().budget_manager.allocation