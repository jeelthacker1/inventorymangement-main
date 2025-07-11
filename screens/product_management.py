import os
import qrcode
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QLineEdit,
                             QComboBox, QDoubleSpinBox, QSpinBox, QTabWidget,
                             QFormLayout, QDialogButtonBox, QFileDialog,
                             QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QBuffer, QByteArray, QIODevice
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QImage
import datetime
import uuid

class ProductManagement(QWidget):
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
        
        title_label = QLabel("Product Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        add_product_btn = QPushButton("Add New Product")
        add_product_btn.setStyleSheet("""
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
        add_product_btn.clicked.connect(self.show_add_product_dialog)
        
        top_bar_layout.addWidget(back_btn)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(add_product_btn)
        
        main_layout.addWidget(top_bar)
        
        # Content area
        content_area = QWidget()
        content_area.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Search and filter bar
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
        self.search_input.setPlaceholderText("Search by product name or ID...")
        self.search_input.setStyleSheet("""
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
        self.search_input.textChanged.connect(self.filter_products)
        
        category_label = QLabel("Category:")
        category_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
        """)
        self.category_filter.currentIndexChanged.connect(self.filter_products)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)  # 1 is the stretch factor
        search_layout.addWidget(category_label)
        search_layout.addWidget(self.category_filter)
        
        content_layout.addWidget(search_frame)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setStyleSheet("""
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
        # Always set 9 columns for consistency, but hide cost price column for employees
        self.products_table.setColumnCount(9)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Name", "Category", "Cost Price", "Selling Price", 
            "Store Qty", "Warehouse Qty", "Total Qty", "Actions"
        ])
        
        # Hide cost price column for employees
        if self.main_window.current_user_role != 'admin':
            self.products_table.hideColumn(3)
        # Set specific column widths - same for both admin and employee views
        header = self.products_table.horizontalHeader()
        
        # Set resize modes for all columns
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Name
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Category
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Cost Price
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Selling Price
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Store Qty
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Warehouse Qty
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Total Qty
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # Actions
        
        # Set column widths
        self.products_table.setColumnWidth(0, 40)   # ID
        self.products_table.setColumnWidth(1, 200)  # Name
        self.products_table.setColumnWidth(2, 80)   # Category
        self.products_table.setColumnWidth(3, 80)   # Cost Price
        self.products_table.setColumnWidth(4, 80)   # Selling Price
        self.products_table.setColumnWidth(5, 70)   # Store Qty
        self.products_table.setColumnWidth(6, 90)   # Warehouse Qty
        self.products_table.setColumnWidth(7, 70)   # Total Qty
        self.products_table.setColumnWidth(8, 130)  # Actions
        
        # For employee view, make the Name column stretch to fill space
        if self.main_window.current_user_role != 'admin':
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        
        content_layout.addWidget(self.products_table)
        
        main_layout.addWidget(content_area)
        
        # Load initial data
        self.refresh_data()
    
    def go_back(self):
        # Check if user is admin or employee and return to the appropriate dashboard
        if self.main_window.current_user_role == 'admin':
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()
    
    def refresh_data(self, selected_product_id=None):
        # Load all products
        products = self.main_window.db_manager.get_all_products()
        
        # Update category filter
        self.update_category_filter(products)
        
        # Populate table
        self.populate_products_table(products, selected_product_id)
    
    def update_category_filter(self, products):
        # Remember current selection
        current_category = self.category_filter.currentText()
        
        # Clear and repopulate categories
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        
        # Extract unique categories
        categories = set()
        for product in products:
            if product['category'] and product['category'].strip():
                categories.add(product['category'])
        
        # Add categories to filter
        for category in sorted(categories):
            self.category_filter.addItem(category)
        
        # Restore previous selection if possible
        index = self.category_filter.findText(current_category)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
    
    def populate_products_table(self, products, selected_product_id=None):
        self.products_table.setRowCount(0)
        selected_row = -1

        for i, product in enumerate(products):
            if not self.product_matches_filter(product):
                continue

            row = self.products_table.rowCount()
            self.products_table.insertRow(row)

            self.set_product_row(row, product)

            if product['id'] == selected_product_id:
                selected_row = row

        if selected_row != -1:
            self.products_table.selectRow(selected_row)
            self.products_table.scrollToItem(self.products_table.item(selected_row, 0))

    def set_product_row(self, row, product):
        is_admin = self.main_window.current_user_role == 'admin'
        
        # Common columns for both admin and employee views
        self.products_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
        self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
        self.products_table.setItem(row, 2, QTableWidgetItem(product.get('category', '')))

        # Column 3: Cost Price (hidden for employees)
        cost_price_item = QTableWidgetItem(f"₹{product['cost_price']:.2f}")
        cost_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.products_table.setItem(row, 3, cost_price_item)
        
        # Column 4: Selling Price
        selling_price_item = QTableWidgetItem(f"₹{product['selling_price']:.2f}")
        selling_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.products_table.setItem(row, 4, selling_price_item)
        
        # Column 5: Store Quantity
        store_qty_item = QTableWidgetItem(str(product['store_quantity']))
        if product['store_quantity'] < product['min_stock_level']:
            store_qty_item.setForeground(QColor('#e74c3c'))
        self.products_table.setItem(row, 5, store_qty_item)
        
        # Column 6: Warehouse Quantity
        warehouse_qty_item = QTableWidgetItem(str(product['warehouse_quantity']))
        self.products_table.setItem(row, 6, warehouse_qty_item)
        
        # Column 7: Total Quantity
        total_qty = product['store_quantity'] + product['warehouse_quantity']
        total_qty_item = QTableWidgetItem(str(total_qty))
        self.products_table.setItem(row, 7, total_qty_item)
        
        # Column 8: Actions - same for both admin and employee views
        actions_widget = self.create_actions_widget(product['id'])
        self.products_table.setCellWidget(row, 8, actions_widget)
    
    def create_actions_widget(self, product_id):
        # Create actions widget with edit and quantity buttons
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(5)
        
        # For all users, show Edit and Qty buttons
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_btn.clicked.connect(lambda checked, p_id=product_id: self.show_edit_product_dialog(p_id))
        actions_layout.addWidget(edit_btn)
        
        # Quantity button
        qty_btn = QPushButton("Qty")
        qty_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        qty_btn.clicked.connect(lambda checked, p_id=product_id: self.show_quantity_dialog(p_id))
        
        actions_layout.addWidget(qty_btn)

        return actions_widget
    
    def product_matches_filter(self, product):
        # Check search text
        search_text = self.search_input.text().lower()
        if search_text:
            if not (search_text in product['name'].lower() or 
                    search_text in str(product['id'])):
                return False
        
        # Check category filter
        selected_category = self.category_filter.currentText()
        if selected_category != "All Categories" and product['category'] != selected_category:
            return False
        
        return True
    
    def filter_products(self):
        # Re-apply filters to current products
        products = self.main_window.db_manager.get_all_products()
        self.populate_products_table(products)
    
    def show_add_product_dialog(self):
        dialog = ProductDialog(self, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the products table
            self.refresh_data(dialog.product_id)
    
    def show_edit_product_dialog(self, product_id):
        dialog = ProductDialog(self, self.main_window, product_id)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the products table
            self.refresh_data(product_id)
    
    def show_quantity_dialog(self, product_id):
        dialog = QuantityDialog(self, self.main_window, product_id)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the products table
            self.refresh_data(product_id)

class ProductDialog(QDialog):
    def __init__(self, parent, main_window, product_id=None):
        super().__init__(parent)
        self.main_window = main_window
        self.product_id = product_id
        self.product = None
        
        if product_id:
            self.product = self.main_window.db_manager.get_product(product_id)
            self.setWindowTitle("Edit Product")
        else:
            self.setWindowTitle("Add New Product")
        
        self.init_ui()
        self.load_product_data()
    
    def init_ui(self):
        self.setMinimumWidth(500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Form layout for product details
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(20)
        
        # Product name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        form_layout.addRow("Product Name:", self.name_input)
        
        # Category
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setPlaceholderText("Select or enter category")
        self.load_categories()
        form_layout.addRow("Category:", self.category_input)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter product description")
        form_layout.addRow("Description:", self.description_input)
        
        # Cost Price (admin only)
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 1000000)
        self.cost_price_input.setDecimals(2)
        self.cost_price_input.setSingleStep(1)
        self.cost_price_input.setPrefix("₹")
        
        # Only show cost price to admin
        if self.main_window.current_user_role == 'admin':
            form_layout.addRow("Cost Price:", self.cost_price_input)
        else:
            # For employees, set a hidden cost price input with default value
            self.cost_price_input.setVisible(False)
            # If editing, preserve the original cost price
            if self.product:
                self.cost_price_input.setValue(self.product['cost_price'])
        
        # Selling Price
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setRange(0, 1000000)
        self.selling_price_input.setDecimals(2)
        self.selling_price_input.setSingleStep(1)
        self.selling_price_input.setPrefix("₹")
        form_layout.addRow("Selling Price:", self.selling_price_input)
        
        # Max Discount
        self.max_discount_input = QDoubleSpinBox()
        self.max_discount_input.setRange(0, 100)
        self.max_discount_input.setDecimals(2)
        self.max_discount_input.setSingleStep(1)
        self.max_discount_input.setSuffix("%")
        form_layout.addRow("Max Discount:", self.max_discount_input)
        
        # Min Stock Level
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 1000)
        self.min_stock_input.setSingleStep(1)
        form_layout.addRow("Min Stock Level:", self.min_stock_input)
        
        # Warehouse Quantity (only for new products)
        if not self.product_id:
            self.warehouse_qty_input = QSpinBox()
            self.warehouse_qty_input.setRange(0, 10000)
            self.warehouse_qty_input.setSingleStep(1)
            form_layout.addRow("Initial Warehouse Qty:", self.warehouse_qty_input)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addSpacing(20)
        main_layout.addWidget(button_box)
    
    def load_categories(self):
        # Get all products to extract categories
        products = self.main_window.db_manager.get_all_products()
        
        # Extract unique categories
        categories = set()
        for product in products:
            if product['category'] and product['category'].strip():
                categories.add(product['category'])
        
        # Add categories to combobox
        for category in sorted(categories):
            self.category_input.addItem(category)
    
    def load_product_data(self):
        if not self.product:
            # Default values for new product
            self.min_stock_input.setValue(5)  # Default min stock level
            return
        
        # Fill form with product data
        self.name_input.setText(self.product['name'])
        
        if self.product['category']:
            index = self.category_input.findText(self.product['category'])
            if index >= 0:
                self.category_input.setCurrentIndex(index)
            else:
                self.category_input.setCurrentText(self.product['category'])
        
        if self.product['description']:
            self.description_input.setText(self.product['description'])
        
        self.cost_price_input.setValue(self.product['cost_price'])
        self.selling_price_input.setValue(self.product['selling_price'])
        self.max_discount_input.setValue(self.product['max_discount'])
        self.min_stock_input.setValue(self.product['min_stock_level'])
    
    def accept(self):
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name is required.")
            return
        
        if self.selling_price_input.value() < self.cost_price_input.value():
            reply = QMessageBox.question(
                self, "Price Warning", 
                "Selling price is less than cost price. This will result in a loss. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Collect product data
        product_data = {
            'name': self.name_input.text().strip(),
            'category': self.category_input.currentText().strip(),
            'description': self.description_input.text().strip(),
            'cost_price': self.cost_price_input.value(),
            'selling_price': self.selling_price_input.value(),
            'max_discount': self.max_discount_input.value(),
            'min_stock_level': self.min_stock_input.value()
        }
        
        if self.product_id:
            # Update existing product
            self.main_window.db_manager.update_product(self.product_id, product_data)
        else:
            # Add new product
            product_data['warehouse_quantity'] = self.warehouse_qty_input.value()
            self.product_id = self.main_window.db_manager.add_product(product_data)
        
        super().accept()

class QuantityDialog(QDialog):
    def __init__(self, parent, main_window, product_id):
        super().__init__(parent)
        self.main_window = main_window
        self.product_id = product_id
        self.product = self.main_window.db_manager.get_product(product_id)
        
        self.setWindowTitle(f"Manage Quantity: {self.product['name']}")
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumWidth(600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Current quantities
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        
        # Store quantity info
        store_qty_label = QLabel(f"Store Quantity: {self.product['store_quantity']}")
        store_qty_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        
        # Warehouse quantity info
        warehouse_qty_label = QLabel(f"Warehouse Quantity: {self.product['warehouse_quantity']}")
        warehouse_qty_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        
        info_layout.addWidget(store_qty_label)
        info_layout.addStretch()
        info_layout.addWidget(warehouse_qty_label)
        
        main_layout.addWidget(info_frame)
        
        # Tab widget for different operations
        tab_widget = QTabWidget()
        
        # Tab 1: Move from warehouse to store
        move_tab = QWidget()
        move_layout = QVBoxLayout(move_tab)
        
        move_description = QLabel(
            "Move items from warehouse to store. This will generate QR codes for the items moved to the store."
        )
        move_description.setWordWrap(True)
        move_description.setStyleSheet("color: #7f8c8d;")
        move_layout.addWidget(move_description)
        
        move_form = QFormLayout()
        move_form.setVerticalSpacing(10)
        
        self.move_qty_input = QSpinBox()
        self.move_qty_input.setRange(0, self.product['warehouse_quantity'])
        self.move_qty_input.setSingleStep(1)
        move_form.addRow("Quantity to Move:", self.move_qty_input)
        
        move_layout.addLayout(move_form)
        
        move_btn = QPushButton("Move to Store & Generate QR Codes")
        move_btn.setStyleSheet("""
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
        move_btn.clicked.connect(self.move_to_store)
        move_layout.addWidget(move_btn)
        
        # Tab 2: Add to warehouse
        restock_tab = QWidget()
        restock_layout = QVBoxLayout(restock_tab)
        
        restock_description = QLabel(
            "Add new items to the warehouse inventory (e.g., when receiving new stock)."
        )
        restock_description.setWordWrap(True)
        restock_description.setStyleSheet("color: #7f8c8d;")
        restock_layout.addWidget(restock_description)
        
        restock_form = QFormLayout()
        restock_form.setVerticalSpacing(10)
        
        self.restock_qty_input = QSpinBox()
        self.restock_qty_input.setRange(1, 10000)
        self.restock_qty_input.setSingleStep(1)
        restock_form.addRow("Quantity to Add:", self.restock_qty_input)
        
        restock_layout.addLayout(restock_form)
        
        restock_btn = QPushButton("Add to Warehouse")
        restock_btn.setStyleSheet("""
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
        restock_btn.clicked.connect(self.add_to_warehouse)
        restock_layout.addWidget(restock_btn)
        
        # Add tabs to tab widget
        tab_widget.addTab(move_tab, "Move to Store")
        tab_widget.addTab(restock_tab, "Add to Warehouse")
        
        main_layout.addWidget(tab_widget)
        
        # QR code preview area (initially hidden)
        self.qr_preview_frame = QFrame()
        self.qr_preview_frame.setVisible(False)
        self.qr_preview_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        qr_preview_layout = QVBoxLayout(self.qr_preview_frame)
        
        qr_preview_label = QLabel("Generated QR Codes")
        qr_preview_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        qr_preview_layout.addWidget(qr_preview_label)
        
        # Scroll area for QR codes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white;")
        
        self.qr_container = QWidget()
        self.qr_layout = QGridLayout(self.qr_container)
        
        scroll_area.setWidget(self.qr_container)
        qr_preview_layout.addWidget(scroll_area)
        
        # Save QR codes button
        save_qr_btn = QPushButton("Save All QR Codes")
        save_qr_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        save_qr_btn.clicked.connect(self.save_qr_codes)
        qr_preview_layout.addWidget(save_qr_btn)
        
        main_layout.addWidget(self.qr_preview_frame)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        
        main_layout.addSpacing(20)
        main_layout.addWidget(button_box)
    
    def move_to_store(self):
        qty_to_move = self.move_qty_input.value()
        
        if qty_to_move <= 0:
            QMessageBox.warning(self, "Invalid Quantity", "Please enter a quantity greater than zero.")
            return
        
        if qty_to_move > self.product['warehouse_quantity']:
            QMessageBox.warning(self, "Invalid Quantity", "Cannot move more items than available in warehouse.")
            return
        
        # Generate QR codes
        qr_code_paths = self.generate_qr_codes(qty_to_move)
        
        # Update database
        new_store_qty = self.product['store_quantity'] + qty_to_move
        new_warehouse_qty = self.product['warehouse_quantity'] - qty_to_move
        
        self.main_window.db_manager.update_product_quantities(
            self.product_id, new_store_qty, new_warehouse_qty
        )
        
        # Add product items with QR codes
        self.main_window.db_manager.add_product_items(
            self.product_id, qty_to_move, qr_code_paths
        )
        
        # Update product reference
        self.product = self.main_window.db_manager.get_product(self.product_id)
        
        # Show success message
        QMessageBox.information(
            self, "Success", 
            f"{qty_to_move} items moved from warehouse to store. QR codes generated."
        )
        
        # Update UI
        self.update_quantity_labels()
        self.move_qty_input.setMaximum(self.product['warehouse_quantity'])
        self.move_qty_input.setValue(0)
    
    def add_to_warehouse(self):
        qty_to_add = self.restock_qty_input.value()
        
        if qty_to_add <= 0:
            QMessageBox.warning(self, "Invalid Quantity", "Please enter a quantity greater than zero.")
            return
        
        # Update database
        new_warehouse_qty = self.product['warehouse_quantity'] + qty_to_add
        
        self.main_window.db_manager.update_product_quantities(
            self.product_id, self.product['store_quantity'], new_warehouse_qty
        )
        
        # Update product reference
        self.product = self.main_window.db_manager.get_product(self.product_id)
        
        # Show success message
        QMessageBox.information(
            self, "Success", 
            f"{qty_to_add} items added to warehouse inventory."
        )
        
        # Update UI
        self.update_quantity_labels()
        self.move_qty_input.setMaximum(self.product['warehouse_quantity'])
        self.restock_qty_input.setValue(1)
    
    def update_quantity_labels(self):
        # Find and update the quantity labels
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QFrame):
                for j in range(widget.layout().count()):
                    item = widget.layout().itemAt(j)
                    if item.widget() and isinstance(item.widget(), QLabel):
                        label = item.widget()
                        if "Store Quantity:" in label.text():
                            label.setText(f"Store Quantity: {self.product['store_quantity']}")
                        elif "Warehouse Quantity:" in label.text():
                            label.setText(f"Warehouse Quantity: {self.product['warehouse_quantity']}")
    
    def generate_qr_codes(self, quantity):
        # Clear existing QR codes
        self.clear_qr_layout()
        
        qr_code_paths = []
        self.qr_images = []  # Store QR images to prevent garbage collection
        
        # Create directory for QR codes if it doesn't exist
        qr_dir = os.path.join(os.getcwd(), 'assets', 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        
        # Generate QR codes
        for i in range(quantity):
            # Generate a unique 12-character ID for the item
            unique_id = f"P{self.product_id}I{i+1}-{uuid.uuid4().hex[:8]}"
            
            # Create a JSON object with product information
            product_data = {
                "item_id": unique_id,
                "product_id": self.product_id,
                "name": self.product['name'],
                "price": self.product['selling_price'],
                "category": self.product['category']
            }
            
            # Convert to JSON string
            qr_data = json.dumps(product_data)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to file
            qr_path = os.path.join(qr_dir, f"{unique_id}.png")
            qr_img.save(qr_path)
            qr_code_paths.append(qr_path)
            
            # Convert to QPixmap for display
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            qr_img.save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.data())
            buffer.close()
            
            # Add to layout
            self.add_qr_to_layout(pixmap, unique_id, i)
            
            # Store image to prevent garbage collection
            self.qr_images.append(pixmap)
        
        # Show QR preview frame
        self.qr_preview_frame.setVisible(True)
        
        return qr_code_paths
    
    def add_qr_to_layout(self, pixmap, unique_id, index):
        # Calculate row and column
        col = index % 3
        row = index // 3
        
        # Create a group box for each QR code
        group_box = QGroupBox()
        group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
        """)
        group_layout = QVBoxLayout(group_box)
        
        # QR code image
        qr_label = QLabel()
        qr_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
        qr_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(qr_label)
        
        # Unique ID label
        id_label = QLabel(unique_id)
        id_label.setAlignment(Qt.AlignCenter)
        id_label.setStyleSheet("font-size: 10px; font-family: monospace;")
        id_label.setWordWrap(True)
        group_layout.addWidget(id_label)
        
        self.qr_layout.addWidget(group_box, row, col)
    
    def clear_qr_layout(self):
        # Remove all widgets from QR layout
        while self.qr_layout.count():
            item = self.qr_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def save_qr_codes(self):
        # Ask for directory to save QR codes
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Save QR Codes", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not directory:
            return
        
        # Copy QR codes to selected directory
        qr_dir = os.path.join(os.getcwd(), 'assets', 'qr_codes')
        
        # Get all QR codes for this product
        product_items = self.main_window.db_manager.get_product_items(self.product_id, 'in_store')
        
        if not product_items:
            QMessageBox.warning(self, "No QR Codes", "No QR codes found for this product.")
            return
        
        # Copy files
        import shutil
        copied_count = 0
        
        for item in product_items:
            if item['qr_code_path'] and os.path.exists(item['qr_code_path']):
                dest_path = os.path.join(directory, os.path.basename(item['qr_code_path']))
                shutil.copy2(item['qr_code_path'], dest_path)
                copied_count += 1
        
        QMessageBox.information(
            self, "QR Codes Saved", 
            f"{copied_count} QR codes saved to {directory}"
        )
    
    def accept(self):
        super().accept()