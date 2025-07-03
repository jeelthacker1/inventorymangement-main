import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QLineEdit,
                             QComboBox, QDoubleSpinBox, QSpinBox, QTabWidget,
                             QFormLayout, QDialogButtonBox, QFileDialog,
                             QScrollArea, QGroupBox, QCheckBox, QRadioButton,
                             QButtonGroup, QDateEdit, QTextEdit, QCompleter,
                             QCalendarWidget)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QStandardItemModel, QStandardItem

class RepairScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
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
        
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #3498db;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        title_label = QLabel("Repair Service Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        add_repair_btn = QPushButton("New Repair Job")
        add_repair_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_repair_btn.clicked.connect(self.show_add_repair_dialog)
        
        top_bar_layout.addWidget(back_btn)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(add_repair_btn)
        
        main_layout.addWidget(top_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Tab widget for different repair statuses
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Create tabs for different repair statuses
        self.pending_tab = QWidget()
        self.in_progress_tab = QWidget()
        self.completed_tab = QWidget()
        self.all_repairs_tab = QWidget()
        
        self.setup_repair_tab(self.pending_tab, "pending")
        self.setup_repair_tab(self.in_progress_tab, "in_progress")
        self.setup_repair_tab(self.completed_tab, "completed")
        self.setup_repair_tab(self.all_repairs_tab, "all")
        
        self.tab_widget.addTab(self.pending_tab, "Pending")
        self.tab_widget.addTab(self.in_progress_tab, "In Progress")
        self.tab_widget.addTab(self.completed_tab, "Completed")
        self.tab_widget.addTab(self.all_repairs_tab, "All Repairs")
        
        content_layout.addWidget(self.tab_widget)
        
        main_layout.addWidget(content_widget)
        
        # Load initial data
        self.refresh_data()
        
        # Set up timer to refresh data every 5 minutes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # 5 minutes in milliseconds
    
    def go_back(self):
        # Check if user is admin or employee and return to the appropriate dashboard
        if self.main_window.current_user_role == 'admin':
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()
    
    def setup_repair_tab(self, tab, status):
        # Layout for the tab
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Search and filter bar
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search by job ID, customer name, or device...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        # Store the search input in the tab for later access
        tab.search_input = search_input
        search_input.textChanged.connect(lambda: self.filter_repairs(tab, status))
        
        date_range_label = QLabel("Date Range:")
        date_range_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate().addMonths(-1))  # Default to 1 month ago
        start_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        
        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate())
        end_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        
        # Store the date filters in the tab for later access
        tab.start_date = start_date
        tab.end_date = end_date
        
        start_date.dateChanged.connect(lambda: self.filter_repairs(tab, status))
        end_date.dateChanged.connect(lambda: self.filter_repairs(tab, status))
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input, 1)  # 1 is the stretch factor
        search_layout.addWidget(date_range_label)
        search_layout.addWidget(start_date)
        search_layout.addWidget(QLabel("to"))
        search_layout.addWidget(end_date)
        
        tab_layout.addWidget(search_frame)
        
        # Repairs table
        repairs_table = QTableWidget()
        repairs_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        repairs_table.setColumnCount(8)
        repairs_table.setHorizontalHeaderLabels([
            "ID", "Customer", "Device", "Issue", "Status", "Received Date", "Estimated Completion", "Actions"
        ])
        repairs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        repairs_table.setAlternatingRowColors(True)
        repairs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        repairs_table.setSelectionBehavior(QTableWidget.SelectRows)
        repairs_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Store the table in the tab for later access
        tab.repairs_table = repairs_table
        
        tab_layout.addWidget(repairs_table)
    
    def refresh_data(self):
        # Refresh data for all tabs
        self.load_repairs_data(self.pending_tab, "pending")
        self.load_repairs_data(self.in_progress_tab, "in_progress")
        self.load_repairs_data(self.completed_tab, "completed")
        self.load_repairs_data(self.all_repairs_tab, "all")
    
    def load_repairs_data(self, tab, status):
        # Get repairs from database based on status
        if status == "all":
            repairs = self.main_window.db_manager.get_all_repairs()
        else:
            repairs = self.main_window.db_manager.get_repairs_by_status(status)
        
        # Apply filters
        self.filter_repairs(tab, status, repairs)
    
    def filter_repairs(self, tab, status, repairs=None):
        # If repairs not provided, get from database
        if repairs is None:
            if status == "all":
                repairs = self.main_window.db_manager.get_all_repairs()
            else:
                repairs = self.main_window.db_manager.get_repairs_by_status(status)
        
        # Get filter values
        search_text = tab.search_input.text().strip().lower()
        start_date = tab.start_date.date().toString("yyyy-MM-dd")
        end_date = tab.end_date.date().toString("yyyy-MM-dd")
        
        # Filter repairs
        filtered_repairs = []
        for repair in repairs:
            # Check if repair matches search text
            if search_text and not (
                search_text in str(repair['id']).lower() or
                search_text in repair['customer_name'].lower() or
                search_text in repair['device'].lower() or
                search_text in repair['issue'].lower()
            ):
                continue
            
            # Check if repair is within date range
            repair_date = repair['received_date'].split()[0]  # Get just the date part
            if repair_date < start_date or repair_date > end_date:
                continue
            
            filtered_repairs.append(repair)
        
        # Update table with filtered repairs
        self.update_repairs_table(tab.repairs_table, filtered_repairs)
    
    def update_repairs_table(self, table, repairs):
        # Clear existing data
        table.setRowCount(0)
        
        # Populate table
        for row, repair in enumerate(repairs):
            table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(repair['id']))
            table.setItem(row, 0, id_item)
            
            # Customer
            table.setItem(row, 1, QTableWidgetItem(repair['customer_name']))
            
            # Device
            table.setItem(row, 2, QTableWidgetItem(repair['product_description']))
            
            # Issue
            issue_item = QTableWidgetItem(repair['issue_description'])
            issue_item.setToolTip(repair['issue_description'])  # Show full issue on hover
            table.setItem(row, 3, issue_item)
            
            # Status
            status_item = QTableWidgetItem(repair['status'].replace('_', ' ').title())
            
            # Set status color
            if repair['status'] == 'pending':
                status_item.setForeground(QColor('#e74c3c'))  # Red
            elif repair['status'] == 'in_progress':
                status_item.setForeground(QColor('#f39c12'))  # Orange
            else:  # completed
                status_item.setForeground(QColor('#2ecc71'))  # Green
            
            table.setItem(row, 4, status_item)
            
            # Received Date
            received_date = repair['received_date'].split()[0]  # Get just the date part
            table.setItem(row, 5, QTableWidgetItem(received_date))
            
            # Estimated Completion
            if repair['estimated_completion_date']:
                est_completion = repair['estimated_completion_date'].split()[0]  # Get just the date part
                table.setItem(row, 6, QTableWidgetItem(est_completion))
            else:
                table.setItem(row, 6, QTableWidgetItem("Not set"))
            
            # Actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            # View/Edit button
            view_btn = QPushButton("View/Edit")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            view_btn.clicked.connect(lambda checked, r_id=repair['id']: self.show_repair_details(r_id))
            
            actions_layout.addWidget(view_btn)
            
            # Add Complete button for pending and in_progress repairs
            if repair['status'] != 'completed':
                complete_btn = QPushButton("Complete")
                complete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 4px;
                        padding: 5px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
                complete_btn.clicked.connect(lambda checked, r_id=repair['id']: self.show_complete_repair_dialog(r_id))
                actions_layout.addWidget(complete_btn)
            
            table.setCellWidget(row, 7, actions_widget)
    
    def show_add_repair_dialog(self):
        dialog = RepairDialog(self, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the repairs data
            self.refresh_data()
            
            # Switch to the Pending tab
            self.tab_widget.setCurrentIndex(0)
    
    def show_repair_details(self, repair_id):
        dialog = RepairDialog(self, self.main_window, repair_id)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the repairs data
            self.refresh_data()
    
    def show_complete_repair_dialog(self, repair_id):
        dialog = CompleteRepairDialog(self, self.main_window, repair_id)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the repairs data
            self.refresh_data()
            
            # Switch to the Completed tab
            self.tab_widget.setCurrentIndex(2)

class RepairDialog(QDialog):
    def __init__(self, parent, main_window, repair_id=None):
        super().__init__(parent)
        self.main_window = main_window
        self.repair_id = repair_id
        self.repair = None
        self.repair_parts = []
        
        if repair_id:
            self.repair = self.main_window.db_manager.get_repair(repair_id)
            self.repair_parts = self.main_window.db_manager.get_repair_parts(repair_id)
            self.setWindowTitle(f"Repair Job #{repair_id}")
        else:
            self.setWindowTitle("New Repair Job")
        
        self.init_ui()
        self.load_repair_data()
    
    def init_ui(self):
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Tab widget for different sections
        tab_widget = QTabWidget()
        
        # Customer and Device Info tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        # Customer section
        customer_group = QGroupBox("Customer Information")
        customer_layout = QFormLayout(customer_group)
        customer_layout.setVerticalSpacing(10)
        
        # Customer search/selection
        customer_search_layout = QHBoxLayout()
        
        customer_search_label = QLabel("Search Customer:")
        
        self.customer_search_input = QLineEdit()
        self.customer_search_input.setPlaceholderText("Search by name or phone...")
        
        # Set up completer for customer search
        self.customer_completer_model = QStandardItemModel()
        self.customer_completer = QCompleter()
        self.customer_completer.setModel(self.customer_completer_model)
        self.customer_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.customer_completer.setFilterMode(Qt.MatchContains)
        self.customer_search_input.setCompleter(self.customer_completer)
        
        self.customer_search_input.textChanged.connect(self.search_customers)
        self.customer_completer.activated.connect(self.select_customer_from_completer)
        
        new_customer_btn = QPushButton("New Customer")
        new_customer_btn.setStyleSheet("""
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
        new_customer_btn.clicked.connect(self.show_new_customer_dialog)
        
        customer_search_layout.addWidget(self.customer_search_input)
        customer_search_layout.addWidget(new_customer_btn)
        
        customer_layout.addRow(customer_search_label, customer_search_layout)
        
        # Customer details
        self.customer_id = None  # To store selected customer ID
        
        self.customer_name_label = QLabel("Not selected")
        self.customer_phone_label = QLabel("")
        self.customer_email_label = QLabel("")
        
        customer_layout.addRow("Name:", self.customer_name_label)
        customer_layout.addRow("Phone:", self.customer_phone_label)
        customer_layout.addRow("Email:", self.customer_email_label)
        
        info_layout.addWidget(customer_group)
        
        # Device section
        device_group = QGroupBox("Device Information")
        device_layout = QFormLayout(device_group)
        device_layout.setVerticalSpacing(10)
        
        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("e.g., iPhone 12 Pro, Samsung TV, etc.")
        
        self.serial_number_input = QLineEdit()
        self.serial_number_input.setPlaceholderText("Device serial number or IMEI")
        
        self.issue_input = QTextEdit()
        self.issue_input.setPlaceholderText("Describe the issue with the device...")
        self.issue_input.setMinimumHeight(100)
        
        device_layout.addRow("Device:", self.device_input)
        device_layout.addRow("Serial Number:", self.serial_number_input)
        device_layout.addRow("Issue:", self.issue_input)
        
        info_layout.addWidget(device_group)
        
        # Repair details section
        repair_group = QGroupBox("Repair Details")
        repair_layout = QFormLayout(repair_group)
        repair_layout.setVerticalSpacing(10)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "In Progress", "Completed"])
        
        self.received_date = QDateEdit()
        self.received_date.setCalendarPopup(True)
        self.received_date.setDate(QDate.currentDate())
        
        self.estimated_completion_date = QDateEdit()
        self.estimated_completion_date.setCalendarPopup(True)
        self.estimated_completion_date.setDate(QDate.currentDate().addDays(3))  # Default to 3 days from now
        
        self.technician_input = QLineEdit()
        
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(80)
        
        repair_layout.addRow("Status:", self.status_combo)
        repair_layout.addRow("Received Date:", self.received_date)
        repair_layout.addRow("Estimated Completion:", self.estimated_completion_date)
        repair_layout.addRow("Assigned Technician:", self.technician_input)
        repair_layout.addRow("Notes:", self.notes_input)
        
        info_layout.addWidget(repair_group)
        
        # Parts tab
        parts_tab = QWidget()
        parts_layout = QVBoxLayout(parts_tab)
        
        # Parts table
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(5)
        self.parts_table.setHorizontalHeaderLabels(["Part Name", "Quantity", "Cost", "Total", "Actions"])
        self.parts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.parts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        parts_layout.addWidget(self.parts_table)
        
        # Add part button
        add_part_btn = QPushButton("Add Part")
        add_part_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_part_btn.clicked.connect(self.show_add_part_dialog)
        
        parts_layout.addWidget(add_part_btn)
        
        # Parts summary
        parts_summary_layout = QHBoxLayout()
        
        self.parts_count_label = QLabel("Parts: 0")
        self.parts_count_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.parts_total_label = QLabel("Total: ₹0.00")
        self.parts_total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        parts_summary_layout.addWidget(self.parts_count_label)
        parts_summary_layout.addStretch()
        parts_summary_layout.addWidget(self.parts_total_label)
        
        parts_layout.addLayout(parts_summary_layout)
        
        # Add tabs to tab widget
        tab_widget.addTab(info_tab, "Customer & Device Info")
        tab_widget.addTab(parts_tab, "Parts")
        
        main_layout.addWidget(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addSpacing(20)
        main_layout.addWidget(button_box)
        
        # Load customers for completer
        self.load_customers_for_completer()
        
        # Load parts data if editing existing repair
        if self.repair_id:
            self.update_parts_table()
    
    def load_customers_for_completer(self):
        # Get all customers from database
        customers = self.main_window.db_manager.get_all_customers()
        
        # Clear current model
        self.customer_completer_model.clear()
        
        # Add customers to model
        for customer in customers:
            display_text = f"{customer['name']} - {customer['phone']}"  # Format: Name - Phone
            item = QStandardItem(display_text)
            item.setData(customer['id'], Qt.UserRole)  # Store customer ID as user data
            self.customer_completer_model.appendRow(item)
    
    def search_customers(self):
        # Get search text
        search_text = self.customer_search_input.text().strip().lower()
        
        if not search_text or len(search_text) < 3:
            return
        
        # Search customers in database
        customers = self.main_window.db_manager.search_customers(search_text)
        
        # Clear current model
        self.customer_completer_model.clear()
        
        # Add customers to model
        for customer in customers:
            display_text = f"{customer['name']} - {customer['phone']}"  # Format: Name - Phone
            item = QStandardItem(display_text)
            item.setData(customer['id'], Qt.UserRole)  # Store customer ID as user data
            self.customer_completer_model.appendRow(item)
    
    def select_customer_from_completer(self, text):
        # Find the selected customer in the model
        for i in range(self.customer_completer_model.rowCount()):
            item = self.customer_completer_model.item(i)
            if item.text() == text:
                customer_id = item.data(Qt.UserRole)
                self.load_customer(customer_id)
                break
    
    def load_customer(self, customer_id):
        # Get customer from database
        customer = self.main_window.db_manager.get_customer(customer_id)
        
        if not customer:
            return
        
        # Store customer ID
        self.customer_id = customer_id
        
        # Update customer details display
        self.customer_name_label.setText(customer['name'])
        self.customer_phone_label.setText(customer['phone'])
        self.customer_email_label.setText(customer['email'] or 'N/A')
    
    def show_new_customer_dialog(self):
        from screens.sales import CustomerDialog  # Import here to avoid circular imports
        
        # Show dialog to add new customer
        dialog = CustomerDialog(self, self.main_window)
        
        if dialog.exec_() == QDialog.Accepted:
            # Reload customers for completer
            self.load_customers_for_completer()
            
            # Load the newly added customer
            if dialog.customer_id:
                self.load_customer(dialog.customer_id)
    
    def load_repair_data(self):
        if not self.repair:
            return
        
        # Load customer
        if self.repair['customer_id']:
            self.load_customer(self.repair['customer_id'])
        
        # Load device info
        self.device_input.setText(self.repair['product_description'])
        self.serial_number_input.setText(self.repair['serial_number'] or '')
        self.issue_input.setText(self.repair['issue_description'])
        
        # Load repair details
        status_index = self.status_combo.findText(self.repair['status'].replace('_', ' ').title())
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        
        # Parse dates
        if self.repair['received_date']:
            received_date = QDate.fromString(self.repair['received_date'].split()[0], "yyyy-MM-dd")
            self.received_date.setDate(received_date)
        
        if self.repair['estimated_completion_date']:
            est_completion = QDate.fromString(self.repair['estimated_completion_date'].split()[0], "yyyy-MM-dd")
            self.estimated_completion_date.setDate(est_completion)
        
        self.technician_input.setText(self.repair['assigned_to'] or '')
        self.notes_input.setText(self.repair['notes'] or '')
    
    def show_add_part_dialog(self):
        dialog = AddPartDialog(self, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            # Add part to list
            part_data = dialog.get_part_data()
            self.repair_parts.append(part_data)
            
            # Update parts table
            self.update_parts_table()
    
    def update_parts_table(self):
        # Clear existing data
        self.parts_table.setRowCount(0)
        
        # Populate table
        parts_total = 0
        for row, part in enumerate(self.repair_parts):
            self.parts_table.insertRow(row)
            
            # Part Name
            self.parts_table.setItem(row, 0, QTableWidgetItem(part['name']))
            
            # Quantity
            qty_item = QTableWidgetItem(str(part['quantity']))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 1, qty_item)
            
            # Cost
            cost_item = QTableWidgetItem(f"₹{part['cost']:.2f}")
            cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.parts_table.setItem(row, 2, cost_item)
            
            # Total
            total = part['quantity'] * part['cost']
            parts_total += total
            total_item = QTableWidgetItem(f"₹{total:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.parts_table.setItem(row, 3, total_item)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_part(r))
            
            self.parts_table.setCellWidget(row, 4, remove_btn)
        
        # Update summary
        self.parts_count_label.setText(f"Parts: {len(self.repair_parts)}")
        self.parts_total_label.setText(f"Total: ₹{parts_total:.2f}")
    
    def remove_part(self, row):
        # Remove part from list
        self.repair_parts.pop(row)
        
        # Update parts table
        self.update_parts_table()
    
    def accept(self):
        # Validate inputs
        if not self.customer_id:
            QMessageBox.warning(self, "Validation Error", "Please select a customer.")
            return
        
        if not self.device_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Device information is required.")
            return
        
        if not self.issue_input.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Issue description is required.")
            return
        
        # Collect repair data
        repair_data = {
            'customer_id': self.customer_id,
            'product_description': self.device_input.text().strip(),
            'issue_description': self.issue_input.toPlainText().strip(),
            'serial_number': self.serial_number_input.text().strip(),
            'status': self.status_combo.currentText().lower().replace(' ', '_'),
            'received_date': self.received_date.date().toString("yyyy-MM-dd"),
            'estimated_completion_date': self.estimated_completion_date.date().toString("yyyy-MM-dd"),
            'assigned_to': self.technician_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip(),
            'parts': self.repair_parts,
            'estimated_cost': sum(part['quantity'] * part['cost'] for part in self.repair_parts)
        }
        
        if self.repair_id:
            # Update existing repair
            success = self.main_window.db_manager.update_repair(self.repair_id, repair_data)
        else:
            # Add new repair
            success = self.main_window.db_manager.add_repair(repair_data)
        
        if not success:
            QMessageBox.critical(self, "Error", "Failed to save repair job. Please try again.")
            return
        
        super().accept()

class AddPartDialog(QDialog):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        
        self.setWindowTitle("Add Part")
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumWidth(400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Product selection
        self.product_combo = QComboBox()
        self.load_products()
        form_layout.addRow("Select Product:", self.product_combo)
        
        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 100)
        self.quantity_input.setValue(1)
        form_layout.addRow("Quantity:", self.quantity_input)
        
        # Cost
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 100000)
        self.cost_input.setDecimals(2)
        self.cost_input.setSingleStep(10)
        self.cost_input.setPrefix("₹")
        form_layout.addRow("Cost per Unit:", self.cost_input)
        
        # Total
        self.total_label = QLabel("₹0.00")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        form_layout.addRow("Total Cost:", self.total_label)
        
        # Update total when quantity or cost changes
        self.quantity_input.valueChanged.connect(self.update_total)
        self.cost_input.valueChanged.connect(self.update_total)
        self.product_combo.currentIndexChanged.connect(self.update_product_cost)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addSpacing(20)
        main_layout.addWidget(button_box)
        
        # Initialize total
        self.update_total()
    
    def load_products(self):
        # Get products from database
        products = self.main_window.db_manager.get_all_products()
        
        # Add products to combo box
        for product in products:
            self.product_combo.addItem(product['name'], product['id'])
    
    def update_product_cost(self):
        # Get selected product ID
        product_id = self.product_combo.currentData()
        
        if product_id:
            # Get product details
            product = self.main_window.db_manager.get_product(product_id)
            
            # Update cost input with product price
            if product:
                self.cost_input.setValue(product['price'])
    
    def update_total(self):
        quantity = self.quantity_input.value()
        cost = self.cost_input.value()
        total = quantity * cost
        self.total_label.setText(f"₹{total:.2f}")
    
    def get_part_data(self):
        return {
            'product_id': self.product_combo.currentData(),
            'name': self.product_combo.currentText(),
            'quantity': self.quantity_input.value(),
            'cost': self.cost_input.value(),
            'unit_price': self.cost_input.value()
        }
    
    def accept(self):
        # Validate inputs
        if self.product_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Validation Error", "Please select a product.")
            return
        
        super().accept()

class CompleteRepairDialog(QDialog):
    def __init__(self, parent, main_window, repair_id):
        super().__init__(parent)
        self.main_window = main_window
        self.repair_id = repair_id
        self.repair = self.main_window.db_manager.get_repair(repair_id)
        self.repair_parts = self.main_window.db_manager.get_repair_parts(repair_id)
        
        if not self.repair:
            QMessageBox.critical(self, "Error", "Repair job not found.")
            self.reject()
            return
        
        self.setWindowTitle(f"Complete Repair Job #{repair_id}")
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumWidth(500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Repair summary
        summary_group = QGroupBox("Repair Summary")
        summary_layout = QFormLayout(summary_group)
        
        customer_name = self.repair['customer_name']
        device = self.repair['device']
        issue = self.repair['issue']
        
        summary_layout.addRow("Customer:", QLabel(customer_name))
        summary_layout.addRow("Device:", QLabel(device))
        
        issue_label = QLabel(issue)
        issue_label.setWordWrap(True)
        summary_layout.addRow("Issue:", issue_label)
        
        main_layout.addWidget(summary_group)
        
        # Parts and service charges
        charges_group = QGroupBox("Parts and Service Charges")
        charges_layout = QVBoxLayout(charges_group)
        
        # Parts table
        if self.repair_parts:
            parts_table = QTableWidget()
            parts_table.setColumnCount(4)
            parts_table.setHorizontalHeaderLabels(["Part Name", "Quantity", "Cost", "Total"])
            parts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            parts_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Populate parts table
            parts_total = 0
            for row, part in enumerate(self.repair_parts):
                parts_table.insertRow(row)
                
                # Part Name
                parts_table.setItem(row, 0, QTableWidgetItem(part['name']))
                
                # Quantity
                qty_item = QTableWidgetItem(str(part['quantity']))
                qty_item.setTextAlignment(Qt.AlignCenter)
                parts_table.setItem(row, 1, qty_item)
                
                # Cost
                cost_item = QTableWidgetItem(f"₹{part['cost']:.2f}")
                cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                parts_table.setItem(row, 2, cost_item)
                
                # Total
                total = part['quantity'] * part['cost']
                parts_total += total
                total_item = QTableWidgetItem(f"₹{total:.2f}")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                parts_table.setItem(row, 3, total_item)
            
            charges_layout.addWidget(parts_table)
            
            # Parts total
            parts_total_label = QLabel(f"Parts Total: ₹{parts_total:.2f}")
            parts_total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            parts_total_label.setAlignment(Qt.AlignRight)
            charges_layout.addWidget(parts_total_label)
        else:
            no_parts_label = QLabel("No parts used for this repair.")
            charges_layout.addWidget(no_parts_label)
        
        # Service charge
        service_layout = QHBoxLayout()
        
        service_charge_label = QLabel("Service Charge:")
        service_charge_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.service_charge_input = QDoubleSpinBox()
        self.service_charge_input.setRange(0, 10000)
        self.service_charge_input.setDecimals(2)
        self.service_charge_input.setSingleStep(100)
        self.service_charge_input.setPrefix("₹")
        self.service_charge_input.setValue(500)  # Default service charge
        self.service_charge_input.valueChanged.connect(self.update_total)
        
        service_layout.addWidget(service_charge_label)
        service_layout.addWidget(self.service_charge_input)
        
        charges_layout.addLayout(service_layout)
        
        main_layout.addWidget(charges_group)
        
        # Total and payment
        payment_group = QGroupBox("Payment Information")
        payment_layout = QFormLayout(payment_group)
        
        # Calculate initial total
        parts_total = sum(part['quantity'] * part['cost'] for part in self.repair_parts)
        service_charge = self.service_charge_input.value()
        initial_total = parts_total + service_charge
        
        # Total amount
        self.total_label = QLabel(f"₹{initial_total:.2f}")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        payment_layout.addRow("Total Amount:", self.total_label)
        
        # Payment method
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Card", "UPI", "Bank Transfer"])
        payment_layout.addRow("Payment Method:", self.payment_method_combo)
        
        # Payment status
        self.payment_status_combo = QComboBox()
        self.payment_status_combo.addItems(["Paid", "Pending"])
        payment_layout.addRow("Payment Status:", self.payment_status_combo)
        
        main_layout.addWidget(payment_group)
        
        # Notes
        notes_group = QGroupBox("Completion Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter any notes about the completed repair...")
        self.notes_input.setMinimumHeight(80)
        
        notes_layout.addWidget(self.notes_input)
        
        main_layout.addWidget(notes_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        generate_invoice_btn = QPushButton("Complete & Generate Invoice")
        generate_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        generate_invoice_btn.clicked.connect(self.complete_and_generate_invoice)
        
        complete_only_btn = QPushButton("Complete Only")
        complete_only_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        complete_only_btn.clicked.connect(self.complete_only)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(complete_only_btn)
        button_layout.addWidget(generate_invoice_btn)
        
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
    
    def update_total(self):
        parts_total = sum(part['quantity'] * part['cost'] for part in self.repair_parts)
        service_charge = self.service_charge_input.value()
        total = parts_total + service_charge
        self.total_label.setText(f"₹{total:.2f}")
    
    def complete_only(self):
        # Update repair status to completed
        completion_data = {
            'status': 'completed',
            'completion_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'service_charge': self.service_charge_input.value(),
            'payment_method': self.payment_method_combo.currentText(),
            'payment_status': self.payment_status_combo.currentText().lower(),
            'completion_notes': self.notes_input.toPlainText().strip()
        }
        
        success = self.main_window.db_manager.complete_repair(self.repair_id, completion_data)
        
        if not success:
            QMessageBox.critical(self, "Error", "Failed to complete repair job. Please try again.")
            return
        
        QMessageBox.information(self, "Success", "Repair job marked as completed successfully.")
        self.accept()
    
    def complete_and_generate_invoice(self):
        # First complete the repair
        completion_data = {
            'status': 'completed',
            'completion_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'service_charge': self.service_charge_input.value(),
            'payment_method': self.payment_method_combo.currentText(),
            'payment_status': self.payment_status_combo.currentText().lower(),
            'completion_notes': self.notes_input.toPlainText().strip()
        }
        
        success = self.main_window.db_manager.complete_repair(self.repair_id, completion_data)
        
        if not success:
            QMessageBox.critical(self, "Error", "Failed to complete repair job. Please try again.")
            return
        
        # Generate invoice
        self.main_window.show_repair_invoice(self.repair_id)
        
        self.accept()