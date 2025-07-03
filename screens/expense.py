import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QDateEdit, QDoubleSpinBox, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QDialog, QFormLayout, QGroupBox, QTextEdit, QFrame, QSplitter,
                             QTabWidget, QCalendarWidget, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon

class ExpenseScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_expenses()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title and add button
        title_layout = QHBoxLayout()
        
        title_label = QLabel("Expense Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        add_expense_btn = QPushButton("Add New Expense")
        add_expense_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_expense_btn.clicked.connect(self.show_add_expense_dialog)
        title_layout.addWidget(add_expense_btn)
        
        main_layout.addLayout(title_layout)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range filter
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Date Range:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_range_layout.addWidget(self.start_date)
        
        date_range_layout.addWidget(QLabel("to"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.end_date)
        
        filter_layout.addLayout(date_range_layout)
        
        # Category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(["Rent", "Utilities", "Salaries", "Inventory", "Marketing", "Maintenance", "Other"])
        category_layout.addWidget(self.category_filter)
        
        filter_layout.addLayout(category_layout)
        
        # Apply filter button
        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        apply_filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_filter_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Expenses table
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(6)
        self.expenses_table.setHorizontalHeaderLabels(["Date", "Category", "Description", "Amount", "Created By", "Actions"])
        self.expenses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expenses_table.setAlternatingRowColors(True)
        self.expenses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.expenses_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        main_layout.addWidget(self.expenses_table)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        self.total_expenses_label = QLabel("Total Expenses: ₹0.00")
        self.total_expenses_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        summary_layout.addWidget(self.total_expenses_label)
        
        summary_layout.addStretch()
        
        self.expense_count_label = QLabel("Number of Expenses: 0")
        summary_layout.addWidget(self.expense_count_label)
        
        main_layout.addWidget(summary_frame)
    
    def load_expenses(self):
        # Get date range from filters
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Get category filter
        category = None
        if self.category_filter.currentText() != "All Categories":
            category = self.category_filter.currentText()
        
        # Get expenses from database
        expenses = self.main_window.db_manager.get_expenses(start_date, end_date, category)
        
        # Update table
        self.update_expenses_table(expenses)
        
        # Update summary
        self.update_summary(expenses)
    
    def update_expenses_table(self, expenses):
        self.expenses_table.setRowCount(0)
        
        for row, expense in enumerate(expenses):
            self.expenses_table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(expense['date'])
            self.expenses_table.setItem(row, 0, date_item)
            
            # Category
            self.expenses_table.setItem(row, 1, QTableWidgetItem(expense['category']))
            
            # Description
            self.expenses_table.setItem(row, 2, QTableWidgetItem(expense['description']))
            
            # Amount
            amount_item = QTableWidgetItem(f"₹{expense['amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.expenses_table.setItem(row, 3, amount_item)
            
            # Created By
            created_by = expense.get('created_by') or 'N/A'
            self.expenses_table.setItem(row, 4, QTableWidgetItem(str(created_by)))
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, expense_id=expense['id']: self.edit_expense(expense_id))
            actions_layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, expense_id=expense['id']: self.delete_expense(expense_id))
            actions_layout.addWidget(delete_btn)
            
            # Create a widget to hold the buttons
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            
            self.expenses_table.setCellWidget(row, 5, actions_widget)
    
    def update_summary(self, expenses):
        total_amount = sum(expense['amount'] for expense in expenses)
        self.total_expenses_label.setText(f"Total Expenses: ₹{total_amount:.2f}")
        self.expense_count_label.setText(f"Number of Expenses: {len(expenses)}")
    
    def apply_filters(self):
        self.load_expenses()
    
    def show_add_expense_dialog(self):
        dialog = ExpenseDialog(self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            self.load_expenses()
    
    def edit_expense(self, expense_id):
        # This would open a dialog to edit an expense
        # For now, just show a message
        QMessageBox.information(self, "Edit Expense", f"Edit expense {expense_id}")
    
    def delete_expense(self, expense_id):
        # Ask for confirmation
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    "Are you sure you want to delete this expense?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Delete expense from database
            # For now, just show a message
            QMessageBox.information(self, "Delete Expense", f"Delete expense {expense_id}")


class ExpenseDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("Add New Expense")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form group
        form_group = QGroupBox("Expense Details")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Rent", "Utilities", "Salaries", "Inventory", "Marketing", "Maintenance", "Other"])
        form_layout.addRow("Category:", self.category_combo)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setSingleStep(100)
        self.amount_input.setPrefix("₹")
        form_layout.addRow("Amount:", self.amount_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_input)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Expense")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self.save_expense)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def save_expense(self):
        # Validate inputs
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount greater than zero.")
            return
        
        if not self.description_input.toPlainText().strip():
            QMessageBox.warning(self, "Missing Description", "Please enter a description for the expense.")
            return
        
        # Prepare expense data
        expense_data = {
            'category': self.category_combo.currentText(),
            'description': self.description_input.toPlainText().strip(),
            'amount': self.amount_input.value(),
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'created_by': self.main_window.current_user.get('id') if hasattr(self.main_window, 'current_user') else None
        }
        
        # Add expense to database
        expense_id = self.main_window.db_manager.add_expense(expense_data)
        
        if expense_id:
            QMessageBox.information(self, "Success", "Expense added successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to add expense. Please try again.")