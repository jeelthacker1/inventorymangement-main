import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
import datetime

class EmployeeDashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
        # Set up a timer to refresh data every 5 minutes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # 300,000 ms = 5 minutes
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar with title and logout button
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #2c3e50; color: white;")
        top_bar.setFixedHeight(60)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)
        
        title_label = QLabel("Employee Dashboard")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.main_window.logout)
        
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(logout_btn)
        
        main_layout.addWidget(top_bar)
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
        """)
        
        # Content area
        content_area = QFrame()
        content_area.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Welcome message and date
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        welcome_layout = QHBoxLayout(welcome_frame)
        
        welcome_text = QLabel(f"Welcome, Employee!")
        welcome_text.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        current_date = QLabel(datetime.datetime.now().strftime("%A, %d %B %Y"))
        current_date.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        current_date.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        welcome_layout.addWidget(welcome_text)
        welcome_layout.addStretch()
        welcome_layout.addWidget(current_date)
        
        content_layout.addWidget(welcome_frame)
        
        # Quick action buttons
        quick_actions_label = QLabel("Quick Actions")
        quick_actions_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        content_layout.addWidget(quick_actions_label)
        
        quick_actions_frame = QFrame()
        quick_actions_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        quick_actions_layout = QGridLayout(quick_actions_frame)
        quick_actions_layout.setContentsMargins(20, 20, 20, 20)
        quick_actions_layout.setSpacing(15)
        
        # Create action buttons
        self.create_action_button(quick_actions_layout, "New Sale", "#3498db", 0, 0, self.main_window.show_sales_screen)
        self.create_action_button(quick_actions_layout, "Scan QR Code", "#9b59b6", 0, 1, lambda: self.main_window.show_qr_scanner())
        self.create_action_button(quick_actions_layout, "Repair Service", "#e67e22", 0, 2, self.main_window.show_repair_screen)
        self.create_action_button(quick_actions_layout, "View Products", "#2ecc71", 1, 0, self.main_window.show_product_management)
        self.create_action_button(quick_actions_layout, "Generate Invoice", "#f39c12", 1, 1, self.main_window.show_invoice_generator)
        # self.create_action_button(quick_actions_layout, "Customer Management", "#16a085", 1, 2, self.main_window.show_customer_screen)
        
        content_layout.addWidget(quick_actions_frame)
        
        # Recent sales table
        recent_sales_label = QLabel("Recent Sales")
        recent_sales_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        content_layout.addWidget(recent_sales_label)
        
        self.recent_sales_table = QTableWidget()
        self.recent_sales_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        self.recent_sales_table.setColumnCount(5)
        self.recent_sales_table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Amount", "Date", "Actions"])
        self.recent_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_sales_table.setAlternatingRowColors(True)
        self.recent_sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        content_layout.addWidget(self.recent_sales_table)
        
        # Inventory Tasks Table (Todo List)
        inventory_tasks_label = QLabel("Inventory Tasks")
        inventory_tasks_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        content_layout.addWidget(inventory_tasks_label)
        
        self.inventory_tasks_table = QTableWidget()
        self.inventory_tasks_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        self.inventory_tasks_table.setColumnCount(6)
        self.inventory_tasks_table.setHorizontalHeaderLabels(["ID", "Product", "Store Qty", "Warehouse Qty", "Status", "Actions"])
        self.inventory_tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_tasks_table.setAlternatingRowColors(True)
        self.inventory_tasks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        content_layout.addWidget(self.inventory_tasks_table)
        
        # Pending repairs table
        pending_repairs_label = QLabel("Pending Repairs")
        pending_repairs_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        content_layout.addWidget(pending_repairs_label)
        
        self.pending_repairs_table = QTableWidget()
        self.pending_repairs_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        self.pending_repairs_table.setColumnCount(5)
        self.pending_repairs_table.setHorizontalHeaderLabels(["ID", "Customer", "Product", "Status", "Actions"])
        self.pending_repairs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pending_repairs_table.setAlternatingRowColors(True)
        self.pending_repairs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        content_layout.addWidget(self.pending_repairs_table)
        
        # Set the content area as the widget for the scroll area
        scroll_area.setWidget(content_area)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
        
        # Load initial data
        self.refresh_data()
    
    def create_action_button(self, layout, text, color, row, col, callback):
        button = QPushButton(text)
        button.setMinimumHeight(100)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        button.clicked.connect(callback)
        layout.addWidget(button, row, col)
        return button
    
    def darken_color(self, hex_color):
        # Simple function to darken a hex color for hover effect
        # This is a very basic implementation
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        factor = 0.8  # Darken by 20%
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def refresh_data(self):
        self.load_recent_sales()
        self.load_pending_repairs()
        self.load_inventory_tasks()
    
    def load_recent_sales(self):
        # Clear existing data
        self.recent_sales_table.setRowCount(0)
        
        # Get recent sales from database
        recent_sales = self.main_window.db_manager.get_recent_sales(10)  # Get last 10 sales
        
        # Populate table
        for row, sale in enumerate(recent_sales):
            self.recent_sales_table.insertRow(row)
            
            # Invoice number
            self.recent_sales_table.setItem(row, 0, QTableWidgetItem(sale['invoice_number']))
            
            # Customer name
            customer_name = sale.get('customer_name', 'Walk-in Customer')
            self.recent_sales_table.setItem(row, 1, QTableWidgetItem(customer_name))
            
            # Amount
            amount_item = QTableWidgetItem(f"₹{sale['final_amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.recent_sales_table.setItem(row, 2, amount_item)
            
            # Date
            date_str = datetime.datetime.strptime(sale['created_at'], "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")
            self.recent_sales_table.setItem(row, 3, QTableWidgetItem(date_str))
            
            # Actions button
            view_btn = QPushButton("View Invoice")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            # Use a lambda with a default argument to capture the current sale_id
            view_btn.clicked.connect(lambda checked, sale_id=sale['id']: self.main_window.show_invoice_generator(sale_id))
            
            self.recent_sales_table.setCellWidget(row, 4, view_btn)
    
    def load_pending_repairs(self):
        # Clear existing data
        self.pending_repairs_table.setRowCount(0)
        
        # Get pending repairs from database
        pending_repairs = self.main_window.db_manager.get_pending_repairs()
        
        # Populate table
        for row, repair in enumerate(pending_repairs):
            self.pending_repairs_table.insertRow(row)
            
            # ID
            self.pending_repairs_table.setItem(row, 0, QTableWidgetItem(str(repair['id'])))
            
            # Customer name
            self.pending_repairs_table.setItem(row, 1, QTableWidgetItem(repair['customer_name']))
            
            # Product description
            self.pending_repairs_table.setItem(row, 2, QTableWidgetItem(repair['product_description']))
            
            # Status
            status_item = QTableWidgetItem(repair['status'].replace('_', ' ').title())
            if repair['status'] == 'pending':
                status_item.setForeground(QColor('#e74c3c'))  # Red for pending
            elif repair['status'] == 'in_progress':
                status_item.setForeground(QColor('#f39c12'))  # Orange for in progress
            self.pending_repairs_table.setItem(row, 3, status_item)
            
            # Actions button
            view_btn = QPushButton("View Details")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            # Use a lambda with a default argument to capture the current repair_id
            view_btn.clicked.connect(lambda checked, repair_id=repair['id']: self.view_repair_details(repair_id))
            
            self.pending_repairs_table.setCellWidget(row, 4, view_btn)
    
    def view_repair_details(self, repair_id):
        # Navigate to repair screen and show details for this repair
        self.main_window.show_repair_screen(repair_id)
    
    def load_inventory_tasks(self):
        # Clear existing data
        self.inventory_tasks_table.setRowCount(0)
        
        # Get products that need assembly from warehouse
        assembly_products = self.main_window.db_manager.get_products_needing_assembly()
        
        # Get products with critically low stock
        critical_products = self.main_window.db_manager.get_critical_stock_products()
        
        # Create a set of product IDs to avoid duplicates
        processed_products = set()
        
        # Add critical products first (highest priority)
        row = 0
        for product in critical_products:
            if product['id'] in processed_products:
                continue
                
            processed_products.add(product['id'])
            self.inventory_tasks_table.insertRow(row)
            
            # ID
            self.inventory_tasks_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            
            # Product Name
            self.inventory_tasks_table.setItem(row, 1, QTableWidgetItem(product['name']))
            
            # Store Quantity
            store_qty_item = QTableWidgetItem(str(product['store_quantity']))
            store_qty_item.setForeground(QColor('#e74c3c'))  # Red for critical
            self.inventory_tasks_table.setItem(row, 2, store_qty_item)
            
            # Warehouse Quantity
            warehouse_qty_item = QTableWidgetItem(str(product['warehouse_quantity']))
            warehouse_qty_item.setForeground(QColor('#e74c3c'))  # Red for critical
            self.inventory_tasks_table.setItem(row, 3, warehouse_qty_item)
            
            # Status
            status_item = QTableWidgetItem("CRITICAL - ORDER NOW")
            status_item.setForeground(QColor('#e74c3c'))  # Red for critical
            status_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.inventory_tasks_table.setItem(row, 4, status_item)
            
            # Actions button
            order_btn = QPushButton("Order Stock")
            order_btn.setStyleSheet("""
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
            
            # Use a lambda with a default argument to capture the current product_id
            order_btn.clicked.connect(lambda checked, product_id=product['id']: self.main_window.show_product_management(product_id))
            
            self.inventory_tasks_table.setCellWidget(row, 5, order_btn)
            row += 1
        
        # Add assembly products
        for product in assembly_products:
            if product['id'] in processed_products:
                continue
                
            processed_products.add(product['id'])
            self.inventory_tasks_table.insertRow(row)
            
            # ID
            self.inventory_tasks_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            
            # Product Name
            self.inventory_tasks_table.setItem(row, 1, QTableWidgetItem(product['name']))
            
            # Store Quantity
            store_qty_item = QTableWidgetItem(str(product['store_quantity']))
            store_qty_item.setForeground(QColor('#f39c12'))  # Orange for low
            self.inventory_tasks_table.setItem(row, 2, store_qty_item)
            
            # Warehouse Quantity
            self.inventory_tasks_table.setItem(row, 3, QTableWidgetItem(str(product['warehouse_quantity'])))
            
            # Status
            status_item = QTableWidgetItem("Assemble from Warehouse")
            status_item.setForeground(QColor('#f39c12'))  # Orange for warning
            self.inventory_tasks_table.setItem(row, 4, status_item)
            
            # Actions button
            assemble_btn = QPushButton("Move to Store")
            assemble_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            
            # Use a lambda with a default argument to capture the current product_id
            assemble_btn.clicked.connect(lambda checked, product_id=product['id']: self.move_to_store(product_id))
            
            self.inventory_tasks_table.setCellWidget(row, 5, assemble_btn)
            row += 1
    
    def move_to_store(self, product_id):
        # Get the product details
        product = self.main_window.db_manager.get_product(product_id)
        if not product:
            QMessageBox.warning(self, "Error", "Product not found.")
            return
        
        # Calculate how many to move (move all if less than 5, otherwise move enough to reach 5 in store)
        warehouse_qty = product['warehouse_quantity']
        store_qty = product['store_quantity']
        
        if warehouse_qty <= 0:
            QMessageBox.warning(self, "Error", "No items available in warehouse.")
            return
        
        qty_to_move = min(warehouse_qty, 5 - store_qty) if store_qty < 5 else 1
        
        # Confirm with the user
        confirm = QMessageBox.question(
            self, 
            "Confirm Move", 
            f"Move {qty_to_move} units of {product['name']} from warehouse to store?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Update quantities
            new_store_qty = store_qty + qty_to_move
            new_warehouse_qty = warehouse_qty - qty_to_move
            
            # Update in database
            success = self.main_window.db_manager.update_product_quantities(
                product_id, new_store_qty, new_warehouse_qty
            )
            
            if success:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Successfully moved {qty_to_move} units to store."
                )
                # Refresh the data
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to update quantities.")