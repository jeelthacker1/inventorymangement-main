import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QComboBox, QDateEdit,
                             QTabWidget, QFormLayout, QGroupBox, QRadioButton,
                             QButtonGroup, QFileDialog, QDialog, QLineEdit,
                             QDoubleSpinBox, QSpinBox, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt, QSize, QTimer, QDate, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor

class CustomerScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db_manager = main_window.db_manager
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar with title and back button
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #2c3e50; color: white;")
        top_bar.setFixedHeight(60)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)
        
        title_label = QLabel("Customer Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        top_bar_layout.addWidget(back_btn)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        
        main_layout.addWidget(top_bar)
        
        # Content area
        content_area = QWidget()
        content_area.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Search and filter section
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, phone, or email...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                min-width: 300px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_customers)
        
        filter_label = QLabel("Filter by:")
        filter_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Customers", "Recent Customers", "Top Customers", "Inactive Customers"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self.load_customers)
        
        add_customer_btn = QPushButton("Add New Customer")
        add_customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        add_customer_btn.clicked.connect(self.add_customer)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(filter_label)
        search_layout.addWidget(self.filter_combo)
        search_layout.addStretch()
        search_layout.addWidget(add_customer_btn)
        
        content_layout.addWidget(search_frame)
        
        # Customer table
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(7)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "Address", "Last Purchase", "Actions"])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column
        self.customer_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions column
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customer_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
                font-weight: bold;
            }
        """)
        
        table_layout.addWidget(self.customer_table)
        content_layout.addWidget(table_frame)
        
        # Customer details section
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        details_layout = QVBoxLayout(details_frame)
        
        details_header = QLabel("Customer Details")
        details_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        
        details_layout.addWidget(details_header)
        
        # Customer details content
        details_content = QFrame()
        details_grid = QGridLayout(details_content)
        details_grid.setColumnStretch(1, 1)  # Make the value column stretch
        details_grid.setColumnStretch(3, 1)  # Make the value column stretch
        
        # Left column
        details_grid.addWidget(QLabel("<b>Name:</b>"), 0, 0)
        self.detail_name = QLabel("")
        details_grid.addWidget(self.detail_name, 0, 1)
        
        details_grid.addWidget(QLabel("<b>Phone:</b>"), 1, 0)
        self.detail_phone = QLabel("")
        details_grid.addWidget(self.detail_phone, 1, 1)
        
        details_grid.addWidget(QLabel("<b>Email:</b>"), 2, 0)
        self.detail_email = QLabel("")
        details_grid.addWidget(self.detail_email, 2, 1)
        
        # Right column
        details_grid.addWidget(QLabel("<b>Address:</b>"), 0, 2)
        self.detail_address = QLabel("")
        details_grid.addWidget(self.detail_address, 0, 3)
        
        details_grid.addWidget(QLabel("<b>Last Purchase:</b>"), 1, 2)
        self.detail_last_purchase = QLabel("")
        details_grid.addWidget(self.detail_last_purchase, 1, 3)
        
        details_grid.addWidget(QLabel("<b>Total Purchases:</b>"), 2, 2)
        self.detail_total_purchases = QLabel("")
        details_grid.addWidget(self.detail_total_purchases, 2, 3)
        
        # Notes section
        details_grid.addWidget(QLabel("<b>Notes:</b>"), 3, 0, 1, 1, Qt.AlignTop)
        self.detail_notes = QLabel("")
        self.detail_notes.setWordWrap(True)
        details_grid.addWidget(self.detail_notes, 3, 1, 1, 3)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Customer")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_customer)
        self.edit_btn.setEnabled(False)
        
        self.view_history_btn = QPushButton("View Purchase History")
        self.view_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.view_history_btn.clicked.connect(self.view_purchase_history)
        self.view_history_btn.setEnabled(False)
        
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.view_history_btn)
        button_layout.addStretch()
        
        details_layout.addWidget(details_content)
        details_layout.addLayout(button_layout)
        
        content_layout.addWidget(details_frame)
        
        main_layout.addWidget(content_area)
        
        # Initialize with no customer selected
        self.selected_customer_id = None
        self.clear_customer_details()
    
    def load_customers(self):
        # Clear existing data
        self.customer_table.setRowCount(0)
        
        # Get filter type
        filter_type = self.filter_combo.currentText()
        
        # Get customers based on filter
        if filter_type == "All Customers":
            customers = self.db_manager.get_all_customers()
        elif filter_type == "Recent Customers":
            customers = self.db_manager.get_recent_customers(30)  # Last 30 days
        elif filter_type == "Top Customers":
            customers = self.db_manager.get_top_customers(20)  # Top 20 by purchase amount
        elif filter_type == "Inactive Customers":
            customers = self.db_manager.get_inactive_customers(90)  # No purchase in 90 days
        
        # Populate table
        for row, customer in enumerate(customers):
            self.customer_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(customer['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.customer_table.setItem(row, 0, id_item)
            
            # Name
            self.customer_table.setItem(row, 1, QTableWidgetItem(customer['name']))
            
            # Phone
            self.customer_table.setItem(row, 2, QTableWidgetItem(customer['phone']))
            
            # Email
            self.customer_table.setItem(row, 3, QTableWidgetItem(customer['email'] or ""))
            
            # Address
            address = customer['address'] or ""
            if len(address) > 30:
                address = address[:27] + "..."
            self.customer_table.setItem(row, 4, QTableWidgetItem(address))
            
            # Last Purchase
            last_purchase = customer.get('last_purchase_date') or ""
            self.customer_table.setItem(row, 5, QTableWidgetItem(last_purchase))
            
            # Actions
            actions_cell = QWidget()
            actions_layout = QHBoxLayout(actions_cell)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            view_btn.clicked.connect(lambda checked, c_id=customer['id']: self.view_customer(c_id))
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            edit_btn.clicked.connect(lambda checked, c_id=customer['id']: self.edit_customer(c_id))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, c_id=customer['id']: self.delete_customer(c_id))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.customer_table.setCellWidget(row, 6, actions_cell)
        
        # Update status message
        self.customer_table.setRowCount(len(customers))
    
    def filter_customers(self):
        search_text = self.search_input.text().lower()
        
        for row in range(self.customer_table.rowCount()):
            match_found = False
            
            # Check name, phone, and email columns
            for col in range(1, 4):  # Columns 1, 2, 3 (Name, Phone, Email)
                item = self.customer_table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break
            
            self.customer_table.setRowHidden(row, not match_found)
    
    def view_customer(self, customer_id):
        # Get customer details
        customer = self.db_manager.get_customer_by_id(customer_id)
        if not customer:
            QMessageBox.warning(self, "Customer Not Found", "The selected customer could not be found.")
            return
        
        # Update selected customer ID
        self.selected_customer_id = customer_id
        
        # Update customer details display
        self.detail_name.setText(customer['name'])
        self.detail_phone.setText(customer['phone'])
        self.detail_email.setText(customer['email'] or "N/A")
        self.detail_address.setText(customer['address'] or "N/A")
        
        # Get additional customer info
        purchase_history = self.db_manager.get_customer_purchase_history(customer_id)
        
        if purchase_history:
            last_purchase = purchase_history[0]['date']  # Assuming sorted by date desc
            total_amount = sum(purchase['total_amount'] for purchase in purchase_history)
            self.detail_last_purchase.setText(f"{last_purchase} (₹{purchase_history[0]['total_amount']:.2f})")
            self.detail_total_purchases.setText(f"{len(purchase_history)} purchases (₹{total_amount:.2f})")
        else:
            self.detail_last_purchase.setText("No purchases yet")
            self.detail_total_purchases.setText("0 purchases (₹0.00)")
        
        self.detail_notes.setText(customer['notes'] or "No notes available")
        
        # Enable action buttons
        self.edit_btn.setEnabled(True)
        self.view_history_btn.setEnabled(True)
    
    def clear_customer_details(self):
        self.selected_customer_id = None
        self.detail_name.setText("")
        self.detail_phone.setText("")
        self.detail_email.setText("")
        self.detail_address.setText("")
        self.detail_last_purchase.setText("")
        self.detail_total_purchases.setText("")
        self.detail_notes.setText("")
        
        # Disable action buttons
        self.edit_btn.setEnabled(False)
        self.view_history_btn.setEnabled(False)
    
    def add_customer(self):
        dialog = CustomerDialog(self, self.db_manager)
        if dialog.exec_():
            self.load_customers()
            # Select the newly added customer if available
            if dialog.customer_id:
                self.view_customer(dialog.customer_id)
    
    def edit_customer(self, customer_id=None):
        if customer_id is None:
            customer_id = self.selected_customer_id
        
        if not customer_id:
            return
        
        customer = self.db_manager.get_customer_by_id(customer_id)
        if not customer:
            QMessageBox.warning(self, "Customer Not Found", "The selected customer could not be found.")
            return
        
        dialog = CustomerDialog(self, self.db_manager, customer)
        if dialog.exec_():
            self.load_customers()
            self.view_customer(customer_id)
    
    def delete_customer(self, customer_id):
        # Check if customer has purchase history
        purchase_history = self.db_manager.get_customer_purchase_history(customer_id)
        
        if purchase_history:
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                "This customer has purchase history. Deleting will not remove their purchase records. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
        else:
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                "Are you sure you want to delete this customer?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
        
        if reply == QMessageBox.Yes:
            success = self.db_manager.delete_customer(customer_id)
            if success:
                QMessageBox.information(self, "Success", "Customer deleted successfully.")
                self.load_customers()
                if self.selected_customer_id == customer_id:
                    self.clear_customer_details()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete customer.")
    
    def view_purchase_history(self):
        if not self.selected_customer_id:
            return
        
        customer = self.db_manager.get_customer_by_id(self.selected_customer_id)
        if not customer:
            return
        
        dialog = PurchaseHistoryDialog(self, self.db_manager, customer)
        dialog.exec_()
    
    def go_back(self):
        # Check if user is admin or employee
        if hasattr(self.main_window, 'admin_dashboard'):
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()


class CustomerDialog(QDialog):
    def __init__(self, parent, db_manager, customer=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer = customer
        self.customer_id = None
        
        if customer:
            self.setWindowTitle("Edit Customer")
        else:
            self.setWindowTitle("Add New Customer")
        
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(10)
        
        # Name field
        name_label = QLabel("Name:")
        name_label.setStyleSheet("font-weight: bold;")
        self.name_input = QLineEdit()
        if self.customer:
            self.name_input.setText(self.customer['name'])
        form_layout.addRow(name_label, self.name_input)
        
        # Phone field
        phone_label = QLabel("Phone:")
        phone_label.setStyleSheet("font-weight: bold;")
        self.phone_input = QLineEdit()
        if self.customer:
            self.phone_input.setText(self.customer['phone'])
        form_layout.addRow(phone_label, self.phone_input)
        
        # Email field
        email_label = QLabel("Email:")
        email_label.setStyleSheet("font-weight: bold;")
        self.email_input = QLineEdit()
        if self.customer:
            self.email_input.setText(self.customer['email'] or "")
        form_layout.addRow(email_label, self.email_input)
        
        # Address field
        address_label = QLabel("Address:")
        address_label.setStyleSheet("font-weight: bold;")
        self.address_input = QLineEdit()
        if self.customer:
            self.address_input.setText(self.customer['address'] or "")
        form_layout.addRow(address_label, self.address_input)
        
        # Notes field
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet("font-weight: bold;")
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        if self.customer:
            self.notes_input.setText(self.customer['notes'] or "")
        form_layout.addRow(notes_label, self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        save_btn.clicked.connect(self.save_customer)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def save_customer(self):
        # Validate required fields
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Customer name is required.")
            self.name_input.setFocus()
            return
        
        if not phone:
            QMessageBox.warning(self, "Validation Error", "Phone number is required.")
            self.phone_input.setFocus()
            return
        
        # Get other fields
        email = self.email_input.text().strip() or None
        address = self.address_input.text().strip() or None
        notes = self.notes_input.toPlainText().strip() or None
        
        # Save customer
        if self.customer:  # Update existing customer
            success = self.db_manager.update_customer(
                self.customer['id'], name, phone, email, address, notes
            )
            if success:
                self.customer_id = self.customer['id']
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update customer.")
        else:  # Add new customer
            customer_id = self.db_manager.add_customer(name, phone, email, address, notes)
            if customer_id:
                self.customer_id = customer_id
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add customer.")


class PurchaseHistoryDialog(QDialog):
    def __init__(self, parent, db_manager, customer):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer = customer
        
        self.setWindowTitle(f"Purchase History - {customer['name']}")
        self.setMinimumSize(800, 500)
        
        self.init_ui()
        self.load_purchase_history()
    
    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
            }
            QTableWidget {
                border: none;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Customer info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        
        # Customer details
        details_layout = QVBoxLayout()
        
        name_label = QLabel(f"<b>Name:</b> {self.customer['name']}")
        name_label.setStyleSheet("font-size: 16px;")
        details_layout.addWidget(name_label)
        
        contact_label = QLabel(f"<b>Phone:</b> {self.customer['phone']}")
        if self.customer['email']:
            contact_label.setText(f"<b>Phone:</b> {self.customer['phone']} | <b>Email:</b> {self.customer['email']}")
        details_layout.addWidget(contact_label)
        
        if self.customer['address']:
            address_label = QLabel(f"<b>Address:</b> {self.customer['address']}")
            details_layout.addWidget(address_label)
        
        info_layout.addLayout(details_layout)
        info_layout.addStretch()
        
        # Summary stats
        stats_layout = QVBoxLayout()
        
        self.total_purchases_label = QLabel("<b>Total Purchases:</b> 0")
        stats_layout.addWidget(self.total_purchases_label)
        
        self.total_amount_label = QLabel("<b>Total Amount:</b> ₹0.00")
        stats_layout.addWidget(self.total_amount_label)
        
        self.avg_purchase_label = QLabel("<b>Average Purchase:</b> ₹0.00")
        stats_layout.addWidget(self.avg_purchase_label)
        
        info_layout.addLayout(stats_layout)
        
        layout.addWidget(info_frame)
        
        # Tabs for different purchase types
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # All purchases tab
        all_tab = QWidget()
        all_layout = QVBoxLayout(all_tab)
        
        self.all_table = QTableWidget()
        self.all_table.setColumnCount(7)
        self.all_table.setHorizontalHeaderLabels(["ID", "Date", "Type", "Items", "Amount", "Payment", "Actions"])
        self.all_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.all_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column
        self.all_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions column
        self.all_table.setAlternatingRowColors(True)
        self.all_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        all_layout.addWidget(self.all_table)
        
        # Sales tab
        sales_tab = QWidget()
        sales_layout = QVBoxLayout(sales_tab)
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Date", "Items", "Amount", "Payment", "Status", "Actions"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column
        self.sales_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions column
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        sales_layout.addWidget(self.sales_table)
        
        # Repairs tab
        repairs_tab = QWidget()
        repairs_layout = QVBoxLayout(repairs_tab)
        
        self.repairs_table = QTableWidget()
        self.repairs_table.setColumnCount(7)
        self.repairs_table.setHorizontalHeaderLabels(["ID", "Date", "Device", "Issue", "Status", "Amount", "Actions"])
        self.repairs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.repairs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column
        self.repairs_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions column
        self.repairs_table.setAlternatingRowColors(True)
        self.repairs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        repairs_layout.addWidget(self.repairs_table)
        
        # Add tabs
        self.tabs.addTab(all_tab, "All Purchases")
        self.tabs.addTab(sales_tab, "Sales")
        self.tabs.addTab(repairs_tab, "Repairs")
        
        layout.addWidget(self.tabs)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def load_purchase_history(self):
        # Get purchase history
        purchase_history = self.db_manager.get_customer_purchase_history(self.customer['id'])
        
        # Update summary stats
        total_purchases = len(purchase_history)
        total_amount = sum(purchase['total_amount'] for purchase in purchase_history)
        avg_purchase = total_amount / total_purchases if total_purchases > 0 else 0
        
        self.total_purchases_label.setText(f"<b>Total Purchases:</b> {total_purchases}")
        self.total_amount_label.setText(f"<b>Total Amount:</b> ₹{total_amount:.2f}")
        self.avg_purchase_label.setText(f"<b>Average Purchase:</b> ₹{avg_purchase:.2f}")
        
        # Clear existing data
        self.all_table.setRowCount(0)
        self.sales_table.setRowCount(0)
        self.repairs_table.setRowCount(0)
        
        # Populate tables
        sales_count = 0
        repairs_count = 0
        
        for row, purchase in enumerate(purchase_history):
            # All purchases table
            self.all_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(purchase['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.all_table.setItem(row, 0, id_item)
            
            # Date
            self.all_table.setItem(row, 1, QTableWidgetItem(purchase['date']))
            
            # Type
            self.all_table.setItem(row, 2, QTableWidgetItem(purchase['type']))
            
            # Items
            self.all_table.setItem(row, 3, QTableWidgetItem(str(purchase['num_items'])))
            
            # Amount
            amount_item = QTableWidgetItem(f"₹{purchase['total_amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.all_table.setItem(row, 4, amount_item)
            
            # Payment
            self.all_table.setItem(row, 5, QTableWidgetItem(purchase['payment_method']))
            
            # Actions
            actions_cell = QWidget()
            actions_layout = QHBoxLayout(actions_cell)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            view_btn.clicked.connect(lambda checked, p_id=purchase['id'], p_type=purchase['type']: 
                                    self.view_purchase(p_id, p_type))
            
            actions_layout.addWidget(view_btn)
            self.all_table.setCellWidget(row, 6, actions_cell)
            
            # Type-specific tables
            if purchase['type'] == 'Sale':
                self.sales_table.insertRow(sales_count)
                
                # ID
                id_item = QTableWidgetItem(str(purchase['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.sales_table.setItem(sales_count, 0, id_item)
                
                # Date
                self.sales_table.setItem(sales_count, 1, QTableWidgetItem(purchase['date']))
                
                # Items
                self.sales_table.setItem(sales_count, 2, QTableWidgetItem(str(purchase['num_items'])))
                
                # Amount
                amount_item = QTableWidgetItem(f"₹{purchase['total_amount']:.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(sales_count, 3, amount_item)
                
                # Payment
                self.sales_table.setItem(sales_count, 4, QTableWidgetItem(purchase['payment_method']))
                
                # Status
                self.sales_table.setItem(sales_count, 5, QTableWidgetItem(purchase['status']))
                
                # Actions
                actions_cell = QWidget()
                actions_layout = QHBoxLayout(actions_cell)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                actions_layout.setSpacing(2)
                
                view_btn = QPushButton("View")
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 4px;
                        padding: 3px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                view_btn.clicked.connect(lambda checked, p_id=purchase['id']: 
                                        self.view_purchase(p_id, 'Sale'))
                
                actions_layout.addWidget(view_btn)
                self.sales_table.setCellWidget(sales_count, 6, actions_cell)
                
                sales_count += 1
            
            elif purchase['type'] == 'Repair':
                self.repairs_table.insertRow(repairs_count)
                
                # ID
                id_item = QTableWidgetItem(str(purchase['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.repairs_table.setItem(repairs_count, 0, id_item)
                
                # Date
                self.repairs_table.setItem(repairs_count, 1, QTableWidgetItem(purchase['date']))
                
                # Device
                self.repairs_table.setItem(repairs_count, 2, QTableWidgetItem(purchase.get('device', 'N/A')))
                
                # Issue
                issue = purchase.get('issue', '')
                if len(issue) > 30:
                    issue = issue[:27] + "..."
                self.repairs_table.setItem(repairs_count, 3, QTableWidgetItem(issue))
                
                # Status
                self.repairs_table.setItem(repairs_count, 4, QTableWidgetItem(purchase['status']))
                
                # Amount
                amount_item = QTableWidgetItem(f"₹{purchase['total_amount']:.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.repairs_table.setItem(repairs_count, 5, amount_item)
                
                # Actions
                actions_cell = QWidget()
                actions_layout = QHBoxLayout(actions_cell)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                actions_layout.setSpacing(2)
                
                view_btn = QPushButton("View")
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 4px;
                        padding: 3px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                view_btn.clicked.connect(lambda checked, p_id=purchase['id']: 
                                        self.view_purchase(p_id, 'Repair'))
                
                actions_layout.addWidget(view_btn)
                self.repairs_table.setCellWidget(repairs_count, 6, actions_cell)
                
                repairs_count += 1
    
    def view_purchase(self, purchase_id, purchase_type):
        # This would open the appropriate screen to view the purchase details
        if purchase_type == 'Sale':
            QMessageBox.information(self, "View Sale", f"Opening sale details for ID: {purchase_id}")
            # self.parent().main_window.show_sale_details(purchase_id)
        elif purchase_type == 'Repair':
            QMessageBox.information(self, "View Repair", f"Opening repair details for ID: {purchase_id}")
            # self.parent().main_window.show_repair_details(purchase_id)