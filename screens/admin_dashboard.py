import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QComboBox, QDateEdit,
                             QScrollArea)
from PyQt5.QtCore import Qt, QSize, QTimer, QDate
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from screens.inventory_report import InventoryReportScreen

class AdminDashboard(QWidget):
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
        
        title_label = QLabel("Admin Dashboard")
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
        content_area = QWidget()
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
        
        welcome_text = QLabel(f"Welcome, Admin!")
        welcome_text.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        current_date = QLabel(datetime.datetime.now().strftime("%A, %d %B %Y"))
        current_date.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        current_date.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        welcome_layout.addWidget(welcome_text)
        welcome_layout.addStretch()
        welcome_layout.addWidget(current_date)
        
        content_layout.addWidget(welcome_frame)
        
        # Date filter for analytics
        date_filter_frame = QFrame()
        date_filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        date_filter_layout = QHBoxLayout(date_filter_frame)
        
        date_filter_label = QLabel("Filter Analytics:")
        date_filter_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["Today", "Last 7 Days", "Last 30 Days", "This Month", "This Year", "Custom Range"])
        self.date_range_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        self.date_range_combo.currentIndexChanged.connect(self.date_range_changed)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))  # Default to last 30 days
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.start_date.dateChanged.connect(self.refresh_data)
        
        date_separator = QLabel("to")
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.end_date.dateChanged.connect(self.refresh_data)
        
        # Initially hide date pickers
        self.start_date.setVisible(False)
        date_separator.setVisible(False)
        self.end_date.setVisible(False)
        
        date_filter_layout.addWidget(date_filter_label)
        date_filter_layout.addWidget(self.date_range_combo)
        date_filter_layout.addWidget(self.start_date)
        date_filter_layout.addWidget(date_separator)
        date_filter_layout.addWidget(self.end_date)
        date_filter_layout.addStretch()
        
        content_layout.addWidget(date_filter_frame)
        
        # Quick action buttons
        quick_actions_label = QLabel("Admin Actions")
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
        quick_actions_frame.setMinimumHeight(250)  # Set minimum height to prevent collapsing
        quick_actions_layout = QGridLayout(quick_actions_frame)
        quick_actions_layout.setContentsMargins(20, 20, 20, 20)
        quick_actions_layout.setSpacing(15)
        
        # Create action buttons
        # self.create_action_button(quick_actions_layout, "Product Management", "#3498db", 0, 0, self.main_window.show_product_management)
        self.create_action_button(quick_actions_layout, "View Products", "#2ecc71", 0, 0, self.main_window.show_product_management)
        self.create_action_button(quick_actions_layout, "Sales", "#9b59b6", 0, 1, self.main_window.show_sales_screen)
        self.create_action_button(quick_actions_layout, "Repair Service", "#e67e22", 0, 2, self.main_window.show_repair_screen)
        self.create_action_button(quick_actions_layout, "Analytics", "#2ecc71", 0, 3, self.main_window.show_analytics_screen)
        self.create_action_button(quick_actions_layout, "QR Scanner", "#1abc9c", 1, 0, lambda: self.main_window.show_qr_scanner())
        self.create_action_button(quick_actions_layout, "Generate Invoice", "#f39c12", 1, 1, self.main_window.show_invoice_generator)
        self.create_action_button(quick_actions_layout, "Add Expense", "#e74c3c", 1, 2, self.show_add_expense_dialog)
        self.create_action_button(quick_actions_layout, "Inventory Report", "#34495e", 1, 3, self.generate_inventory_report)
        self.create_action_button(quick_actions_layout, "Customer Management", "#16a085", 2, 0, self.main_window.show_customer_screen)
        
        content_layout.addWidget(quick_actions_frame)
        
        # Analytics section
        analytics_label = QLabel("Business Analytics")
        analytics_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 15px;")
        content_layout.addWidget(analytics_label)
        
        # Create a frame for the analytics charts
        analytics_frame = QFrame()
        analytics_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
            }
        """)
        analytics_frame.setMinimumHeight(900)  # Increased height to accommodate more charts
        analytics_layout = QGridLayout(analytics_frame)
        analytics_layout.setContentsMargins(20, 20, 20, 20)  # Add padding
        analytics_layout.setSpacing(30)  # Increased spacing between charts
        analytics_layout.setVerticalSpacing(40)  # Extra vertical spacing
        
        # Sales chart
        self.sales_figure = Figure(figsize=(5, 4), dpi=100)
        self.sales_canvas = FigureCanvas(self.sales_figure)
        self.sales_canvas.setMinimumHeight(280)  # Increased height
        self.sales_canvas.setMinimumWidth(320)  # Increased width
        sales_frame = QFrame()  # Create a container frame
        sales_frame.setStyleSheet("""
            QFrame {
                background-color: white; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
                padding: 10px;
            }
        """)
        sales_layout = QVBoxLayout(sales_frame)
        sales_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside frame
        sales_layout.setSpacing(10)  # Add spacing between elements
        
        sales_title = QLabel("Sales Trend")
        sales_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        sales_title.setAlignment(Qt.AlignCenter)
        sales_layout.addWidget(sales_title)
        sales_layout.addWidget(self.sales_canvas)
        analytics_layout.addWidget(sales_frame, 0, 0)
        
        # Product performance chart
        self.product_figure = Figure(figsize=(5, 4), dpi=100)
        self.product_canvas = FigureCanvas(self.product_figure)
        self.product_canvas.setMinimumHeight(280)  # Increased height
        self.product_canvas.setMinimumWidth(320)  # Increased width
        product_frame = QFrame()  # Create a container frame
        product_frame.setStyleSheet("""
            QFrame {
                background-color: white; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
                padding: 10px;
            }
        """)
        product_layout = QVBoxLayout(product_frame)
        product_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside frame
        product_layout.setSpacing(10)  # Add spacing between elements
        
        product_title = QLabel("Product Performance")
        product_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        product_title.setAlignment(Qt.AlignCenter)
        product_layout.addWidget(product_title)
        product_layout.addWidget(self.product_canvas)
        analytics_layout.addWidget(product_frame, 0, 1)
        
        # Profit analysis chart
        self.profit_figure = Figure(figsize=(5, 4), dpi=100)
        self.profit_canvas = FigureCanvas(self.profit_figure)
        self.profit_canvas.setMinimumHeight(280)  # Increased height
        self.profit_canvas.setMinimumWidth(320)  # Increased width
        profit_frame = QFrame()  # Create a container frame
        profit_frame.setStyleSheet("""
            QFrame {
                background-color: white; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
                padding: 10px;
            }
        """)
        profit_layout = QVBoxLayout(profit_frame)
        profit_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside frame
        profit_layout.setSpacing(10)  # Add spacing between elements
        
        profit_title = QLabel("Profit Analysis")
        profit_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        profit_title.setAlignment(Qt.AlignCenter)
        profit_layout.addWidget(profit_title)
        profit_layout.addWidget(self.profit_canvas)
        analytics_layout.addWidget(profit_frame, 1, 0)
        
        # Inventory status chart
        self.inventory_figure = Figure(figsize=(5, 4), dpi=100)
        self.inventory_canvas = FigureCanvas(self.inventory_figure)
        self.inventory_canvas.setMinimumHeight(280)  # Increased height
        self.inventory_canvas.setMinimumWidth(320)  # Increased width
        inventory_frame = QFrame()  # Create a container frame
        inventory_frame.setStyleSheet("""
            QFrame {
                background-color: white; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
                padding: 10px;
            }
        """)
        inventory_layout = QVBoxLayout(inventory_frame)
        inventory_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside frame
        inventory_layout.setSpacing(10)  # Add spacing between elements
        
        inventory_title = QLabel("Inventory Status")
        inventory_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        inventory_title.setAlignment(Qt.AlignCenter)
        inventory_layout.addWidget(inventory_title)
        inventory_layout.addWidget(self.inventory_canvas)
        analytics_layout.addWidget(inventory_frame, 1, 1)
        
        # Cost Analysis chart
        self.cost_figure = Figure(figsize=(5, 4), dpi=100)
        self.cost_canvas = FigureCanvas(self.cost_figure)
        self.cost_canvas.setMinimumHeight(280)  # Increased height
        self.cost_canvas.setMinimumWidth(320)  # Increased width
        cost_frame = QFrame()  # Create a container frame
        cost_frame.setStyleSheet("""
            QFrame {
                background-color: white; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
                padding: 10px;
            }
        """)
        cost_layout = QVBoxLayout(cost_frame)
        cost_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside frame
        cost_layout.setSpacing(10)  # Add spacing between elements
        
        cost_title = QLabel("Cost Analysis by Category")
        cost_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        cost_title.setAlignment(Qt.AlignCenter)
        cost_layout.addWidget(cost_title)
        cost_layout.addWidget(self.cost_canvas)
        analytics_layout.addWidget(cost_frame, 2, 0)
        
        # Profit Margin by Category chart
        self.margin_figure = Figure(figsize=(5, 4), dpi=100)
        self.margin_canvas = FigureCanvas(self.margin_figure)
        self.margin_canvas.setMinimumHeight(280)  # Increased height
        self.margin_canvas.setMinimumWidth(320)  # Increased width
        margin_frame = QFrame()  # Create a container frame
        margin_frame.setStyleSheet("""
            QFrame {
                background-color: white; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px;
                padding: 10px;
            }
        """)
        margin_layout = QVBoxLayout(margin_frame)
        margin_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside frame
        margin_layout.setSpacing(10)  # Add spacing between elements
        
        margin_title = QLabel("Profit Margin by Category")
        margin_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        margin_title.setAlignment(Qt.AlignCenter)
        margin_layout.addWidget(margin_title)
        margin_layout.addWidget(self.margin_canvas)
        analytics_layout.addWidget(margin_frame, 2, 1)
        
        content_layout.addWidget(analytics_frame)
        
        # Low stock products table
        content_layout.addSpacing(20)  # Add spacing before section
        low_stock_label = QLabel("Low Stock Products")
        low_stock_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 15px;")
        content_layout.addWidget(low_stock_label)
        content_layout.addSpacing(10)  # Add spacing after label
        
        # Create a container frame for the table
        low_stock_frame = QFrame()
        low_stock_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        low_stock_frame.setMinimumHeight(300)  # Increased minimum height
        low_stock_layout = QVBoxLayout(low_stock_frame)
        low_stock_layout.setContentsMargins(15, 15, 15, 15)  # Add padding
        
        # Add a title inside the frame
        low_stock_inner_title = QLabel("Low Stock Products")
        low_stock_inner_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        low_stock_inner_title.setAlignment(Qt.AlignCenter)  # Center align the title
        low_stock_layout.addWidget(low_stock_inner_title)
        low_stock_layout.addSpacing(10)  # Add spacing after title
        
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e0f0ff;
            }
        """)
        self.low_stock_table.setColumnCount(6)
        self.low_stock_table.setHorizontalHeaderLabels(["ID", "Product Name", "Store Qty", "Warehouse Qty", "Min Level", "Actions"])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.low_stock_table.horizontalHeader().setVisible(True)
        self.low_stock_table.horizontalHeader().setHighlightSections(True)
        self.low_stock_table.setAlternatingRowColors(True)
        self.low_stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.low_stock_table.setMinimumHeight(200)  # Increased minimum height
        
        low_stock_layout.addWidget(self.low_stock_table)
        content_layout.addWidget(low_stock_frame)
        
        # Non-selling products table
        content_layout.addSpacing(20)  # Add spacing before section
        non_selling_label = QLabel("Non-Selling Products (Last 30 Days)")
        non_selling_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 15px;")
        content_layout.addWidget(non_selling_label)
        content_layout.addSpacing(10)  # Add spacing after label
        
        # Create a container frame for the table
        non_selling_frame = QFrame()
        non_selling_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        non_selling_frame.setMinimumHeight(300)  # Increased minimum height
        non_selling_layout = QVBoxLayout(non_selling_frame)
        non_selling_layout.setContentsMargins(15, 15, 15, 15)  # Add padding
        
        # Add a title inside the frame
        non_selling_inner_title = QLabel("Non-Selling Products (Last 30 Days)")
        non_selling_inner_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px;")
        non_selling_inner_title.setAlignment(Qt.AlignCenter)  # Center align the title
        non_selling_layout.addWidget(non_selling_inner_title)
        non_selling_layout.addSpacing(10)  # Add spacing after title
        
        self.non_selling_table = QTableWidget()
        self.non_selling_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e0f0ff;
            }
        """)
        self.non_selling_table.setColumnCount(5)
        self.non_selling_table.setHorizontalHeaderLabels(["ID", "Product Name", "Store Qty", "Price", "Actions"])
        self.non_selling_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.non_selling_table.horizontalHeader().setVisible(True)
        self.non_selling_table.horizontalHeader().setHighlightSections(True)
        self.non_selling_table.setAlternatingRowColors(True)  # Add alternating row colors
        self.non_selling_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table non-editable
        self.non_selling_table.setMinimumHeight(200)  # Set minimum height
        
        non_selling_layout.addWidget(self.non_selling_table)
        content_layout.addWidget(non_selling_frame)
        
        # Set the content area as the widget for the scroll area
        scroll_area.setWidget(content_area)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
        
        # Load initial data
        self.refresh_data()
    
    def create_action_button(self, layout, text, color, row, col, callback):
        button = QPushButton(text)
        button.setMinimumHeight(80)
        button.setMinimumWidth(150)  # Set minimum width
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                font-size: 14px;
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
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        factor = 0.8  # Darken by 20%
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def date_range_changed(self, index):
        today = QDate.currentDate()
        
        # Hide date pickers by default
        self.start_date.setVisible(False)
        self.end_date.setVisible(False)
        
        if index == 0:  # Today
            self.start_date.setDate(today)
            self.end_date.setDate(today)
        elif index == 1:  # Last 7 Days
            self.start_date.setDate(today.addDays(-6))
            self.end_date.setDate(today)
        elif index == 2:  # Last 30 Days
            self.start_date.setDate(today.addDays(-29))
            self.end_date.setDate(today)
        elif index == 3:  # This Month
            self.start_date.setDate(QDate(today.year(), today.month(), 1))
            self.end_date.setDate(today)
        elif index == 4:  # This Year
            self.start_date.setDate(QDate(today.year(), 1, 1))
            self.end_date.setDate(today)
        elif index == 5:  # Custom Range
            self.start_date.setVisible(True)
            self.end_date.setVisible(True)
        
        self.refresh_data()
    
    def refresh_data(self):
        self.load_low_stock_products()
        self.load_non_selling_products()
        self.update_analytics_charts()
    
    def load_low_stock_products(self):
        # Clear existing data
        self.low_stock_table.setRowCount(0)
        
        # Get low stock products from database
        low_stock_products = self.main_window.db_manager.get_low_stock_products()
        
        # Get critical stock products
        critical_products = self.main_window.db_manager.get_critical_stock_products()
        critical_product_ids = {p['id'] for p in critical_products}
        
        # Populate table
        for row, product in enumerate(low_stock_products):
            self.low_stock_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(product['id']))
            self.low_stock_table.setItem(row, 0, id_item)
            
            # Product Name
            product_name_item = QTableWidgetItem(product['name'])
            if product['id'] in critical_product_ids:
                product_name_item.setForeground(QColor('#e74c3c'))  # Red for critical
                product_name_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.low_stock_table.setItem(row, 1, product_name_item)
            
            # Store Quantity
            store_qty_item = QTableWidgetItem(str(product['store_quantity']))
            
            # Apply color based on stock level
            if product['store_quantity'] <= 2:  # Critical store level
                store_qty_item.setForeground(QColor('#e74c3c'))  # Red for critical
                store_qty_item.setFont(QFont("Arial", 9, QFont.Bold))
                store_qty_item.setBackground(QColor(255, 235, 235))  # Light red background
            elif product['store_quantity'] < product['min_stock_level']:
                store_qty_item.setForeground(QColor('#f39c12'))  # Orange for low stock
                store_qty_item.setBackground(QColor(255, 248, 225))  # Light orange background
            
            self.low_stock_table.setItem(row, 2, store_qty_item)
            
            # Warehouse Quantity
            warehouse_qty_item = QTableWidgetItem(str(product['warehouse_quantity']))
            
            # Apply color based on stock level
            if product['warehouse_quantity'] <= 3:  # Critical warehouse level
                warehouse_qty_item.setForeground(QColor('#e74c3c'))  # Red for critical
                warehouse_qty_item.setFont(QFont("Arial", 9, QFont.Bold))
                warehouse_qty_item.setBackground(QColor(255, 235, 235))  # Light red background
            elif product['warehouse_quantity'] < product['min_stock_level']:
                warehouse_qty_item.setForeground(QColor('#f39c12'))  # Orange for low stock
                warehouse_qty_item.setBackground(QColor(255, 248, 225))  # Light orange background
                
            self.low_stock_table.setItem(row, 3, warehouse_qty_item)
            
            # Min Stock Level
            min_stock_item = QTableWidgetItem(str(product['min_stock_level']))
            min_stock_item.setTextAlignment(Qt.AlignCenter)  # Center align the text
            self.low_stock_table.setItem(row, 4, min_stock_item)
            
            # Actions button
            if product['id'] in critical_product_ids:
                # Critical stock - show urgent restock button
                restock_btn = QPushButton("URGENT RESTOCK")
                restock_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        font-weight: bold;
                        border-radius: 4px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
            else:
                # Regular low stock - show normal restock button
                restock_btn = QPushButton("Restock")
                restock_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
            
            # Use a lambda with a default argument to capture the current product_id
            restock_btn.clicked.connect(lambda checked, product_id=product['id']: self.restock_product(product_id))
            
            self.low_stock_table.setCellWidget(row, 5, restock_btn)
    
    def load_non_selling_products(self):
        # Clear existing data
        self.non_selling_table.setRowCount(0)
        
        # Get non-selling products from database
        non_selling_products = self.main_window.db_manager.get_non_selling_products(30, 10)  # Last 30 days, top 10
        
        # Populate table
        for row, product in enumerate(non_selling_products):
            self.non_selling_table.insertRow(row)
            
            # ID
            self.non_selling_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            
            # Product Name
            self.non_selling_table.setItem(row, 1, QTableWidgetItem(product['name']))
            
            # Store Quantity
            self.non_selling_table.setItem(row, 2, QTableWidgetItem(str(product['store_quantity'])))
            
            # Price
            price_item = QTableWidgetItem(f"₹{product['selling_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.non_selling_table.setItem(row, 3, price_item)
            
            # Actions button
            discount_btn = QPushButton("Set Discount")
            discount_btn.setStyleSheet("""
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
            discount_btn.clicked.connect(lambda checked, product_id=product['id']: self.set_product_discount(product_id))
            
            self.non_selling_table.setCellWidget(row, 4, discount_btn)
    
    def update_analytics_charts(self):
        # Get date range
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Update sales chart
        self.update_sales_chart(start_date, end_date)
        
        # Update product performance chart
        self.update_product_performance_chart(start_date, end_date)
        
        # Update profit analysis chart
        self.update_profit_chart(start_date, end_date)
        
        # Update inventory status chart
        self.update_inventory_chart()
        
        # Update cost analysis chart
        self.update_cost_analysis_chart(start_date, end_date)
        
        # Update profit margin by category chart
        self.update_margin_by_category_chart(start_date, end_date)
    
    def update_sales_chart(self, start_date, end_date):
        # Get sales data by day
        sales_data = self.main_window.db_manager.get_sales_by_period('day', start_date, end_date)
        
        # Clear the figure
        self.sales_figure.clear()
        
        # Set figure size and adjust margins for better spacing
        self.sales_figure.subplots_adjust(bottom=0.28, left=0.15, right=0.95, top=0.88)
        
        # Create subplot with adjusted bottom margin for x-axis labels
        ax = self.sales_figure.add_subplot(111)
        
        # Set background color for better visibility
        ax.set_facecolor('#f8f9fa')
        
        if not sales_data:
            ax.text(0.5, 0.5, "No sales data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(facecolor='white', alpha=0.8, pad=10, boxstyle="round,pad=0.5", edgecolor='#e0e0e0'))
        else:
            # Extract dates and sales amounts
            dates = [data['period'] for data in sales_data]
            amounts = [data['final_sales'] for data in sales_data]
            
            # Calculate total sales for display
            total_sales = sum(amounts)
            
            # Format dates for better display
            formatted_dates = []
            for date_str in dates:
                try:
                    # Try to parse and reformat the date
                    date_parts = date_str.split('-')
                    if len(date_parts) == 3:
                        formatted_dates.append(f"{date_parts[2]}/{date_parts[1]}")
                    else:
                        formatted_dates.append(date_str)
                except:
                    formatted_dates.append(date_str)
            
            # Create gradient colors for bars
            colors = []
            base_color = '#3498db'  # Base blue color
            for i in range(len(formatted_dates)):
                # Create slight variation in color for visual interest
                color_factor = 0.7 + (0.3 * (i / max(1, len(formatted_dates) - 1)))
                r, g, b = int(int(base_color[1:3], 16) * color_factor), \
                          int(int(base_color[3:5], 16) * color_factor), \
                          int(int(base_color[5:7], 16) * color_factor)
                colors.append(f'#{r:02x}{g:02x}{b:02x}')
            
            # Plot the data with increased width and spacing
            bars = ax.bar(range(len(formatted_dates)), amounts, color=colors, width=0.75, 
                         edgecolor='#2980b9', linewidth=1, alpha=0.9)
            
            # Add value labels on top of bars with improved formatting
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:  # Only show label if value is greater than 0
                    # Format large numbers with commas for better readability
                    if height >= 1000:
                        value_text = f'₹{int(height):,}'
                    else:
                        value_text = f'₹{int(height)}'
                    
                    # Position label with better spacing
                    label_y_pos = height + (max(amounts) * 0.03)
                    
                    ax.text(bar.get_x() + bar.get_width()/2., label_y_pos,
                           value_text, ha='center', va='bottom', fontsize=9, fontweight='bold',
                           bbox=dict(facecolor='white', alpha=0.8, pad=2, boxstyle="round,pad=0.3", 
                                    edgecolor='#e0e0e0'))
            
            # Add total sales text at the top
            ax.text(0.5, 0.98, f'Total: ₹{total_sales:,}', 
                   horizontalalignment='center', verticalalignment='top',
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(facecolor='#e8f4fc', alpha=0.9, pad=4, boxstyle="round,pad=0.4", 
                            edgecolor='#3498db'))
            
            # Set title and labels with improved styling
            ax.set_title('Daily Sales', fontsize=14, pad=15, fontweight='bold', color='#2c3e50')
            ax.set_ylabel('Amount (₹)', fontsize=12, labelpad=10, fontweight='bold', color='#2c3e50')
            
            # Add grid for better readability
            ax.grid(axis='y', linestyle='--', alpha=0.7, color='#cccccc')
            
            # Remove top and right spines for cleaner look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cccccc')
            ax.spines['bottom'].set_color('#cccccc')
            
            # Format x-axis labels with better visibility
            if len(formatted_dates) > 8:
                step = max(1, len(formatted_dates) // 8)  # Ensure at least 1 step
                ticks = [i for i in range(0, len(formatted_dates), step)]
                ax.set_xticks(ticks)
                ax.set_xticklabels([formatted_dates[i] for i in ticks], rotation=45, ha='right', 
                                  fontsize=10, fontweight='bold')
            else:
                ax.set_xticks(range(len(formatted_dates)))
                ax.set_xticklabels(formatted_dates, rotation=45, ha='right', 
                                  fontsize=10, fontweight='bold')
            
            # Add padding to x-axis labels
            plt.setp(ax.get_xticklabels(), y=0.05)
            
            # Format y-axis with commas for thousands
            ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"₹{int(x):,}"))
            
            # Set y-axis limit with some padding
            if max(amounts) > 0:
                ax.set_ylim(0, max(amounts) * 1.2)
            
            # Add some padding to prevent label cutoff
            ax.margins(x=0.05)
        
        # Use tight_layout with adjusted padding
        self.sales_figure.tight_layout(pad=2.5)
        self.sales_canvas.draw()
    
    def update_product_performance_chart(self, start_date, end_date):
        # Get top selling products
        top_products = self.main_window.db_manager.get_top_selling_products(start_date, end_date, 5)
        
        # Clear the figure
        self.product_figure.clear()
        
        # Set figure size and adjust margins for better spacing
        self.product_figure.subplots_adjust(bottom=0.28, left=0.15, right=0.85, top=0.88)
        
        # Create subplot with adjusted bottom margin for x-axis labels
        ax = self.product_figure.add_subplot(111)
        
        # Set background color for better visibility
        ax.set_facecolor('#f8f9fa')
        
        if not top_products:
            ax.text(0.5, 0.5, "No product data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(facecolor='white', alpha=0.8, pad=10, boxstyle="round,pad=0.5", edgecolor='#e0e0e0'))
        else:
            # Extract product names and quantities
            names = [product['name'] if len(product['name']) <= 15 else product['name'][:12] + '...' 
                    for product in top_products]
            quantities = [product['total_quantity'] for product in top_products]
            revenues = [product['total_revenue'] for product in top_products]
            
            # Create x positions with more spacing
            x = np.arange(len(names))
            width = 0.35  # Adjusted width for better visibility
            
            # Create gradient colors for bars
            quantity_colors = ['#3498db', '#2980b9', '#1f618d', '#154360', '#0b2d3d'][:len(names)]
            revenue_colors = ['#e74c3c', '#c0392b', '#922b21', '#641e16', '#3d1210'][:len(names)]
            
            # Plot the data with improved styling
            quantity_bars = ax.bar(x - width/2, quantities, width, label='Quantity', 
                                  color=quantity_colors, edgecolor='#2980b9', linewidth=1, alpha=0.9)
            ax2 = ax.twinx()
            revenue_bars = ax2.bar(x + width/2, revenues, width, label='Revenue', 
                                 color=revenue_colors, edgecolor='#c0392b', linewidth=1, alpha=0.9)
            
            # Add value labels on top of bars with improved styling
            for bar in quantity_bars:
                height = bar.get_height()
                if height > 0:  # Only show label if value is greater than 0
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold',
                           bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2", edgecolor='#d4d4d4'))
            
            for bar in revenue_bars:
                height = bar.get_height()
                if height > 0:  # Only show label if value is greater than 0
                    ax2.text(bar.get_x() + bar.get_width()/2., height + (max(revenues) * 0.02 if revenues else 0),
                            f'₹{int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold',
                            bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2", edgecolor='#d4d4d4'))
            
            # Set labels and title with improved styling
            ax.set_title('Top Selling Products', fontsize=14, fontweight='bold', pad=15)
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10)  # Set the tick labels
            ax.set_ylabel('Quantity Sold', fontsize=12, fontweight='bold', labelpad=10)
            ax2.set_ylabel('Revenue (₹)', fontsize=12, fontweight='bold', labelpad=10)
            
            # Add grid for better readability
            ax.grid(True, axis='y', linestyle='--', alpha=0.3)
            
            # Remove top and right spines for cleaner look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax2.spines['top'].set_visible(False)
            
            # Add legend with better positioning and styling
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            legend = ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
                      frameon=True, framealpha=0.9, facecolor='white', edgecolor='#d4d4d4')
            
            # Add more bottom padding for x-axis labels and prevent label cutoff
            plt.subplots_adjust(bottom=0.25)
            ax.margins(x=0.05)
        
        # Use tight_layout with adjusted padding
        self.product_figure.tight_layout(pad=2.0)
        self.product_canvas.draw()
    
    def update_profit_chart(self, start_date, end_date):
        # Get profit analysis data
        profit_data = self.main_window.db_manager.get_profit_analysis(start_date, end_date)
        
        # Clear the figure
        self.profit_figure.clear()
        
        # Set figure size and adjust margins for better spacing
        self.profit_figure.subplots_adjust(bottom=0.25, left=0.15, right=0.95, top=0.88)
        
        # Create subplot with adjusted bottom margin for x-axis labels
        ax = self.profit_figure.add_subplot(111)
        
        # Set background color for better visibility
        ax.set_facecolor('#f8f9fa')
        
        if not profit_data or profit_data['total_revenue'] == 0:
            ax.text(0.5, 0.5, "No profit data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(facecolor='white', alpha=0.8, pad=10, boxstyle="round,pad=0.5", edgecolor='#e0e0e0'))
        else:
            # Extract data
            labels = ['Revenue', 'Cost', 'Expenses', 'Gross Profit', 'Net Profit']
            values = [
                profit_data['total_revenue'] or 0,
                profit_data['total_cost'] or 0,
                profit_data['total_expenses'] or 0,
                profit_data['gross_profit'] or 0,
                profit_data['net_profit'] or 0
            ]
            
            # Enhanced colors with better contrast
            colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6']
            edge_colors = ['#2980b9', '#c0392b', '#d35400', '#27ae60', '#8e44ad']
            
            # Plot the data with improved styling
            bars = ax.bar(labels, values, color=colors, width=0.6, 
                         edgecolor=edge_colors, linewidth=1.5, alpha=0.9)
            
            # Set labels and title with improved styling
            ax.set_title('Profit Analysis', fontsize=14, fontweight='bold', pad=15)
            ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold', labelpad=10)
            ax.tick_params(axis='x', labelsize=10, labelrotation=0, pad=8)
            
            # Format y-axis with commas for thousands
            ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"₹{int(x):,}"))
            
            # Add value labels on top of bars with improved styling
            for bar in bars:
                height = bar.get_height()
                # Format large numbers with commas for better readability
                if height >= 1000:
                    value_text = f'₹{int(height):,}'
                else:
                    value_text = f'₹{height:.2f}'
                
                # Add background to value labels for better visibility
                ax.text(bar.get_x() + bar.get_width()/2., height + (max(values) * 0.02),
                       value_text, ha='center', va='bottom', fontsize=9, fontweight='bold',
                       bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2", edgecolor='#d4d4d4'))
            
            # Add margins and profit percentage with improved styling
            margin_box = dict(facecolor='white', alpha=0.9, boxstyle="round,pad=0.5", 
                             edgecolor='#ddd', linewidth=1.5)
            
            # Add a title for the margin box
            ax.text(0.02, 0.98, "Profit Margins:", transform=ax.transAxes,
                   fontsize=11, fontweight='bold')
            
            # Add margin percentages with color indicators
            gross_color = '#2ecc71' if profit_data['gross_margin'] > 0 else '#e74c3c'
            net_color = '#2ecc71' if profit_data['net_margin'] > 0 else '#e74c3c'
            
            ax.text(0.02, 0.92, f"Gross Margin: {profit_data['gross_margin']:.1f}%", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', color=gross_color,
                   bbox=margin_box)
            ax.text(0.02, 0.85, f"Net Margin: {profit_data['net_margin']:.1f}%", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', color=net_color,
                   bbox=margin_box)
            
            # Remove top and right spines for cleaner look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Add grid for better readability
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            # Add some padding to prevent label cutoff
            ax.margins(x=0.05, y=0.1)
        
        # Use tight_layout with adjusted padding
        self.profit_figure.tight_layout(pad=2.0)
        self.profit_canvas.draw()
    
    def update_inventory_chart(self):
        # Get all products
        products = self.main_window.db_manager.get_all_products()
        
        # Clear the figure
        self.inventory_figure.clear()
        
        # Set figure size and adjust margins for better spacing
        self.inventory_figure.subplots_adjust(bottom=0.28, left=0.15, right=0.95, top=0.88)
        
        # Create subplot with adjusted margins
        ax = self.inventory_figure.add_subplot(111)
        
        # Set background color for better visibility
        ax.set_facecolor('#f8f9fa')
        
        if not products:
            ax.text(0.5, 0.5, "No inventory data available", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(facecolor='white', alpha=0.8, pad=10, boxstyle="round,pad=0.5", edgecolor='#e0e0e0'))
        else:
            # Calculate total store and warehouse quantities
            total_store = sum(product['store_quantity'] for product in products)
            total_warehouse = sum(product['warehouse_quantity'] for product in products)
            
            # Group products by category
            categories = {}
            for product in products:
                category = product['category'] or 'Uncategorized'
                if category not in categories:
                    categories[category] = {'store': 0, 'warehouse': 0}
                categories[category]['store'] += product['store_quantity']
                categories[category]['warehouse'] += product['warehouse_quantity']
            
            # Extract category names and quantities
            cat_names = list(categories.keys())
            store_quantities = [categories[cat]['store'] for cat in cat_names]
            warehouse_quantities = [categories[cat]['warehouse'] for cat in cat_names]
            
            # Create x positions with improved spacing
            x = np.arange(len(cat_names))
            width = 0.35  # Adjusted width for better visibility
            
            # Create gradient colors for bars
            store_colors = ['#3498db', '#2980b9', '#1f618d', '#154360', '#0b2d3d'][:len(cat_names)]
            warehouse_colors = ['#2ecc71', '#27ae60', '#229954', '#1e8449', '#196f3d'][:len(cat_names)]
            
            # Plot the data with improved styling
            store_bars = ax.bar(x - width/2, store_quantities, width, label='Store', 
                               color='#3498db', edgecolor='#2980b9', linewidth=1, alpha=0.9)
            warehouse_bars = ax.bar(x + width/2, warehouse_quantities, width, label='Warehouse', 
                                  color='#2ecc71', edgecolor='#27ae60', linewidth=1, alpha=0.9)
            
            # Set labels and title with improved styling
            ax.set_title('Inventory by Category', fontsize=14, fontweight='bold', pad=15)
            ax.set_xticks(x)
            ax.set_xticklabels(cat_names, rotation=45, ha='right', fontsize=10)  # Set the tick labels
            ax.set_ylabel('Quantity', fontsize=12, fontweight='bold', labelpad=10)
            
            # Add value labels on top of bars with improved styling
            max_height = max(max(store_quantities or [0]), max(warehouse_quantities or [0]))
            label_offset = max_height * 0.03 if max_height > 0 else 0.5
            
            for bar in store_bars:
                height = bar.get_height()
                if height > 0:  # Only show labels for non-zero values
                    ax.text(bar.get_x() + bar.get_width()/2., height + label_offset,
                           f'{int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold',
                           bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2", edgecolor='#d4d4d4'))
                    
            for bar in warehouse_bars:
                height = bar.get_height()
                if height > 0:  # Only show labels for non-zero values
                    ax.text(bar.get_x() + bar.get_width()/2., height + label_offset,
                           f'{int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold',
                           bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2", edgecolor='#d4d4d4'))
            
            # Add grid for better readability
            ax.grid(True, axis='y', linestyle='--', alpha=0.3)
            
            # Remove top and right spines for cleaner look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Add legend with better positioning and styling
            legend = ax.legend(loc='upper right', frameon=True, framealpha=0.9, 
                             facecolor='white', edgecolor='#d4d4d4')
            
            # Add total inventory text with improved styling
            total_box = dict(facecolor='white', alpha=0.9, boxstyle="round,pad=0.5", 
                           edgecolor='#ddd', linewidth=1.5)
            
            # Add a title for the totals box
            ax.text(0.02, 0.98, "Inventory Totals:", transform=ax.transAxes,
                   fontsize=11, fontweight='bold')
            
            ax.text(0.02, 0.92, f"Total Store: {total_store:,}", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', color='#3498db',
                   bbox=total_box)
            ax.text(0.02, 0.85, f"Total Warehouse: {total_warehouse:,}", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', color='#2ecc71',
                   bbox=total_box)
            
            # Add some padding to prevent label cutoff
            ax.margins(x=0.05, y=0.1)
        
        # Use tight_layout with adjusted padding
        self.inventory_figure.tight_layout(pad=2.0)
        self.inventory_canvas.draw()
    
    def restock_product(self, product_id):
        # This would open a dialog to restock the product
        # For now, we'll just navigate to the product management screen
        self.main_window.show_product_management(product_id)
    
    def set_product_discount(self, product_id):
        # This would open a dialog to set a discount for the product
        # For now, we'll just navigate to the product management screen
        self.main_window.show_product_management(product_id)
    
    def show_add_expense_dialog(self):
        # Show the expense screen which has the add expense functionality
        self.main_window.show_expense_screen()
    
    def update_cost_analysis_chart(self, start_date, end_date):
        # Get product categories and their cost data
        categories = []
        total_costs = []
        
        # Get all products
        products = self.main_window.db_manager.get_all_products()
        
        # Group products by category and calculate total cost
        category_costs = {}
        for product in products:
            category = product['category'] or 'Uncategorized'
            cost_price = float(product['cost_price'] or 0)
            store_qty = int(product['store_quantity'] or 0)
            warehouse_qty = int(product['warehouse_quantity'] or 0)
            total_qty = store_qty + warehouse_qty
            total_cost = cost_price * total_qty
            
            if category not in category_costs:
                category_costs[category] = 0
            category_costs[category] += total_cost
        
        # Sort categories by total cost (descending)
        sorted_categories = sorted(category_costs.items(), key=lambda x: x[1], reverse=True)
        
        # Extract data for plotting
        for category, cost in sorted_categories:
            categories.append(category)
            total_costs.append(cost)
        
        # Create the plot
        self.cost_figure.clear()
        
        # Set figure size and adjust margins for better spacing
        self.cost_figure.subplots_adjust(left=0.25, right=0.95, top=0.88, bottom=0.15)
        
        ax = self.cost_figure.add_subplot(111)
        
        # Set background color for better visibility
        ax.set_facecolor('#f8f9fa')
        
        # If no data, display a message
        if not categories:
            ax.text(0.5, 0.5, 'No cost data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, pad=10, boxstyle="round,pad=0.5", edgecolor='#e0e0e0'))
            self.cost_canvas.draw()
            return
        
        # Create horizontal bar chart with improved styling
        colors = self.get_color_gradient(len(categories))
        bars = ax.barh(categories, total_costs, color=colors, 
                      edgecolor='#555555', linewidth=0.8, alpha=0.9, height=0.6)
        
        # Add data labels with improved styling
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width * 1.01
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'₹{width:,.2f}',
                    va='center', fontsize=9, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, boxstyle="round,pad=0.2", edgecolor='#d4d4d4'))
        
        # Set labels and title with improved styling
        ax.set_xlabel('Total Cost (₹)', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_title('Inventory Cost by Category', fontsize=14, fontweight='bold', pad=15)
        
        # Format y-axis to show full category names with improved styling
        ax.tick_params(axis='y', labelsize=10, pad=5)
        ax.tick_params(axis='x', labelsize=9, pad=5)
        
        # Format x-axis with commas for thousands
        ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"₹{int(x):,}"))
        
        # Add grid for better readability
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)
        
        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add some padding to prevent label cutoff
        ax.margins(x=0.2, y=0.05)
        
        # Adjust layout and draw
        self.cost_figure.tight_layout(pad=2.0)
        self.cost_canvas.draw()
    
    def update_margin_by_category_chart(self, start_date, end_date):
        # Clear the figure
        self.margin_figure.clear()
        
        # Get sales data grouped by category within date range
        sales_by_category = self.main_window.db_manager.get_sales_by_category(start_date, end_date)
        
        # If no sales data, display a message
        if not sales_by_category:
            ax = self.margin_figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No sales data available for this period', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes)
            self.margin_canvas.draw()
            return
        
        # Prepare data for plotting
        categories = []
        gross_margins = []
        net_margins = []
        
        # Get total expenses for the period
        total_expenses = self.main_window.db_manager.get_total_expenses(start_date, end_date) or 0
        
        for category, data in sales_by_category.items():
            categories.append(category)
            
            # Calculate gross margin percentage
            revenue = data['revenue']
            cost = data['cost']
            gross_profit = revenue - cost
            gross_margin_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
            gross_margins.append(gross_margin_pct)
            
            # Calculate net margin percentage (considering allocated expenses)
            # For simplicity, we'll allocate expenses proportionally to revenue
            total_revenue = sum(d['revenue'] for d in sales_by_category.values())
            expense_allocation = (revenue / total_revenue) * total_expenses if total_revenue > 0 else 0
            net_profit = gross_profit - expense_allocation
            net_margin_pct = (net_profit / revenue * 100) if revenue > 0 else 0
            net_margins.append(net_margin_pct)
        
        # Create the plot
        ax = self.margin_figure.add_subplot(111)
        
        # Set width of bars
        bar_width = 0.35
        index = range(len(categories))
        
        # Create grouped bar chart
        ax.bar([i - bar_width/2 for i in index], gross_margins, bar_width, label='Gross Margin %', color='#3498db')
        ax.bar([i + bar_width/2 for i in index], net_margins, bar_width, label='Net Margin %', color='#2ecc71')
        
        # Set labels and title
        ax.set_xlabel('Category')
        ax.set_ylabel('Margin (%)')
        ax.set_title('Profit Margins by Category')
        ax.set_xticks(index)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        
        # Add a horizontal line at 0%
        ax.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        
        # Add legend
        ax.legend()
        
        # Adjust layout and draw
        self.margin_figure.tight_layout()
        self.margin_canvas.draw()
    
    def get_color_gradient(self, count):
        """Generate a gradient of colors for charts"""
        if count <= 0:
            return []
        
        # Use a colorful gradient
        return plt.cm.viridis(np.linspace(0, 0.8, count))
    
    def generate_inventory_report(self):
        # Import InventoryReportScreen from inventory_report.py
        from screens.inventory_report import InventoryReportScreen
        
        # Create and show the inventory report screen
        inventory_report = InventoryReportScreen(self.main_window)
        
        # Add the inventory report screen to the stacked widget if it's not already there
        if not hasattr(self.main_window, 'inventory_report_screen'):
            self.main_window.inventory_report_screen = inventory_report
            self.main_window.stacked_widget.addWidget(inventory_report)
        
        # Show the inventory report screen
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.inventory_report_screen)