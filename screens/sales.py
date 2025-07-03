import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QLineEdit,
                             QComboBox, QDoubleSpinBox, QSpinBox, QTabWidget,
                             QFormLayout, QDialogButtonBox, QFileDialog,
                             QScrollArea, QGroupBox, QCheckBox, QRadioButton,
                             QButtonGroup, QDateEdit, QCompleter, QApplication)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QDate, QModelIndex
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QStandardItemModel, QStandardItem

class SalesScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.cart_items = []  # List to store items in the cart
        self.customer = None  # Current customer
        self.init_ui()
        
    def refresh_data(self):
        """Refresh the sales screen data"""
        print("DEBUG: Refreshing sales screen data")
        
        # Clear the product search input and results
        self.product_search_input.clear()
        self.product_results.setRowCount(0)
        
        # Clear the cart
        self.cart_items = []
        self.update_cart_display()
        
        # Clear customer selection
        self.customer = None
        self.customer_details_frame.setVisible(False)
        
        # Reset customer search input
        self.customer_search_input.clear()
        
        # Reload customer data for autocomplete
        self.load_customers_for_completer()
        
        # Update cart summary
        self.update_cart_summary()
    
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
        
        title_label = QLabel("Sales")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        top_bar_layout.addWidget(back_btn)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        
        main_layout.addWidget(top_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Left panel - Product scanning and cart
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(15)
        
        # Product scanning section
        scan_frame = QFrame()
        scan_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        scan_layout = QVBoxLayout(scan_frame)
        scan_layout.setContentsMargins(10, 10, 10, 10)
        scan_layout.setSpacing(10)
        
        scan_title = QLabel("Add Products")
        scan_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        scan_layout.addWidget(scan_title)
        
        # Product search
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Search products by name, code, or category")
        self.product_search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.product_search_input.returnPressed.connect(self.search_products)
        
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("""
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
        search_btn.clicked.connect(self.search_products)
        
        search_layout.addWidget(self.product_search_input, 4)  # 4/5 of the width
        search_layout.addWidget(search_btn, 1)  # 1/5 of the width
        
        scan_layout.addLayout(search_layout)
        
        # Product ID input
        id_layout = QHBoxLayout()
        id_layout.setSpacing(10)
        
        self.product_id_input = QLineEdit()
        self.product_id_input.setPlaceholderText("Enter product ID or scan QR code")
        self.product_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.product_id_input.returnPressed.connect(self.add_product_by_id)
        
        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_product_by_id)
        
        scan_btn = QPushButton("Scan QR")
        scan_btn.setStyleSheet("""
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
        scan_btn.clicked.connect(self.show_qr_scanner)
        
        id_layout.addWidget(self.product_id_input, 3)  # 3/5 of the width
        id_layout.addWidget(add_btn, 1)  # 1/5 of the width
        id_layout.addWidget(scan_btn, 1)  # 1/5 of the width
        
        scan_layout.addLayout(id_layout)
        
        # Product search results
        results_label = QLabel("Search Results:")
        results_label.setStyleSheet("font-weight: bold;")
        scan_layout.addWidget(results_label)
        
        self.product_results = QTableWidget()
        self.product_results.setColumnCount(5)
        self.product_results.setHorizontalHeaderLabels(["ID", "Name", "Price", "Stock", "Actions"])
        self.product_results.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        self.product_results.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch name column
        self.product_results.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_results.setEditTriggers(QTableWidget.NoEditTriggers)
        self.product_results.setAlternatingRowColors(True)
        self.product_results.verticalHeader().setVisible(False)
        
        scan_layout.addWidget(self.product_results)
        
        left_layout.addWidget(scan_frame, 1)  # 1/2 of the height
        
        # Cart section
        cart_frame = QFrame()
        cart_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        cart_layout = QVBoxLayout(cart_frame)
        cart_layout.setContentsMargins(10, 10, 10, 10)
        cart_layout.setSpacing(10)
        
        cart_header_layout = QHBoxLayout()
        cart_header_layout.setSpacing(10)
        
        cart_title = QLabel("Shopping Cart")
        cart_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        clear_cart_btn = QPushButton("Clear Cart")
        clear_cart_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_cart_btn.clicked.connect(self.clear_cart)
        
        cart_header_layout.addWidget(cart_title)
        cart_header_layout.addStretch()
        cart_header_layout.addWidget(clear_cart_btn)
        
        cart_layout.addLayout(cart_header_layout)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Qty", "Total", "Actions"])
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch name column
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.verticalHeader().setVisible(False)
        
        cart_layout.addWidget(self.cart_table)
        
        # Cart summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(10, 10, 10, 10)
        summary_layout.setSpacing(5)
        
        self.items_count_label = QLabel("Items: 0")
        self.subtotal_label = QLabel("Subtotal: ₹0.00")
        self.discount_label = QLabel("Discount: ₹0.00")
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        
        summary_layout.addWidget(self.items_count_label)
        summary_layout.addWidget(self.subtotal_label)
        summary_layout.addWidget(self.discount_label)
        summary_layout.addWidget(self.total_label)
        
        cart_layout.addWidget(summary_frame)
        
        left_layout.addWidget(cart_frame, 1)  # 1/2 of the height
        
        # Right panel - Customer and payment
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Customer section
        customer_frame = QFrame()
        customer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        customer_layout = QVBoxLayout(customer_frame)
        customer_layout.setContentsMargins(10, 10, 10, 10)
        customer_layout.setSpacing(10)
        
        customer_title = QLabel("Customer Information")
        customer_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        customer_layout.addWidget(customer_title)
        
        # Customer search
        customer_search_layout = QHBoxLayout()
        customer_search_layout.setSpacing(10)
        
        self.customer_search_input = QLineEdit()
        self.customer_search_input.setPlaceholderText("Search customer by name or phone")
        self.customer_search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Set up customer completer
        self.customer_completer_model = QStandardItemModel()
        completer = QCompleter(self.customer_completer_model, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setMaxVisibleItems(10)  # Show more items in the dropdown
        
        # Connect multiple signals for better responsiveness
        completer.activated[str].connect(self.select_customer_from_completer)
        completer.highlighted[str].connect(self.on_customer_highlighted)
        
        # Also connect the QModelIndex version for direct clicks
        completer.activated[QModelIndex].connect(self.on_completer_activated_index)
        
        self.customer_search_input.setCompleter(completer)
        
        # Connect various input events
        self.customer_search_input.returnPressed.connect(self.on_search_return_pressed)
        self.customer_search_input.editingFinished.connect(self.on_editing_finished)
        
        # Connect search signal
        self.customer_search_input.textChanged.connect(self.search_customers)
        
        # Load all customers initially with a slight delay to ensure UI is ready
        QTimer.singleShot(300, self.load_customers_for_completer)
        
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
        
        customer_search_layout.addWidget(self.customer_search_input, 3)  # 3/4 of the width
        customer_search_layout.addWidget(new_customer_btn, 1)  # 1/4 of the width
        
        customer_layout.addLayout(customer_search_layout)
        
        # Customer details
        self.customer_details_frame = QFrame()
        self.customer_details_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
                padding: 10px;
            }
        """)
        self.customer_details_layout = QVBoxLayout(self.customer_details_frame)
        self.customer_details_layout.setContentsMargins(10, 10, 10, 10)
        self.customer_details_layout.setSpacing(5)
        
        # Initially hide the customer details frame
        self.customer_details_frame.setVisible(False)
        
        # Initialize customer variable
        self.customer = None
        
        clear_customer_btn = QPushButton("Clear Customer")
        clear_customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_customer_btn.clicked.connect(self.clear_customer)
        
        self.customer_details_layout.addWidget(clear_customer_btn, alignment=Qt.AlignRight)
        
        customer_layout.addWidget(self.customer_details_frame)
        self.customer_details_frame.setVisible(False)  # Hide initially
        
        right_layout.addWidget(customer_frame)
        
        # Payment section
        payment_frame = QFrame()
        payment_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        payment_layout = QVBoxLayout(payment_frame)
        payment_layout.setContentsMargins(10, 10, 10, 10)
        payment_layout.setSpacing(10)
        
        payment_title = QLabel("Payment Information")
        payment_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        payment_layout.addWidget(payment_title)
        
        # Discount
        discount_layout = QHBoxLayout()
        discount_layout.setSpacing(10)
        
        discount_label = QLabel("Discount (%)")
        discount_label.setStyleSheet("font-weight: bold;")
        
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setValue(0)
        self.discount_input.setSingleStep(1)
        self.discount_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.discount_input.valueChanged.connect(self.update_cart_summary)
        
        discount_layout.addWidget(discount_label)
        discount_layout.addWidget(self.discount_input)
        
        payment_layout.addLayout(discount_layout)
        
        # GST option
        gst_layout = QHBoxLayout()
        gst_layout.setSpacing(10)
        
        gst_label = QLabel("Include GST (18%)")
        gst_label.setStyleSheet("font-weight: bold;")
        
        self.include_gst_checkbox = QCheckBox()
        self.include_gst_checkbox.setChecked(True)
        self.include_gst_checkbox.stateChanged.connect(self.update_cart_summary)
        
        gst_layout.addWidget(gst_label)
        gst_layout.addWidget(self.include_gst_checkbox)
        
        payment_layout.addLayout(gst_layout)
        
        # Payment method
        payment_method_layout = QHBoxLayout()
        payment_method_layout.setSpacing(10)
        
        payment_method_label = QLabel("Payment Method")
        payment_method_label.setStyleSheet("font-weight: bold;")
        
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Card", "UPI", "Bank Transfer"])
        self.payment_method_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
        """)
        
        payment_method_layout.addWidget(payment_method_label)
        payment_method_layout.addWidget(self.payment_method_combo)
        
        payment_layout.addLayout(payment_method_layout)
        
        # Checkout button
        checkout_btn = QPushButton("Complete Sale & Generate Invoice")
        checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        checkout_btn.clicked.connect(self.complete_sale)
        
        payment_layout.addSpacing(20)
        payment_layout.addWidget(checkout_btn)
        
        right_layout.addWidget(payment_frame)
        
        # Set layout proportions
        content_layout.addWidget(left_panel, 3)  # 3/5 of the width
        content_layout.addWidget(right_panel, 2)  # 2/5 of the width
        
        main_layout.addWidget(content_widget)
        
        # Load initial data
        self.load_customers_for_completer()
    
    def go_back(self):
        # Check if user is admin or employee and return to the appropriate dashboard
        if self.main_window.current_user_role == 'admin':
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()
    
    def show_qr_scanner(self):
        # Show QR scanner screen
        self.main_window.show_qr_scanner(callback=self.process_qr_code)
    
    def process_qr_code(self, qr_data):
        # Process QR code data
        if qr_data:
            self.product_id_input.setText(qr_data)
            self.add_product_by_id()
    
    def add_product_by_id(self):
        # Get product ID from input
        product_id_text = self.product_id_input.text().strip()
        
        if not product_id_text:
            return
        
        # Check if it's a product item ID (with format P{product_id}I{item_id})
        if 'I' in product_id_text and product_id_text.startswith('P'):
            parts = product_id_text.split('I')
            if len(parts) == 2 and parts[0].startswith('P'):
                try:
                    product_id = int(parts[0][1:])
                    item_id = int(parts[1])
                    
                    # Get product and item details
                    product = self.main_window.db_manager.get_product(product_id)
                    product_item = self.main_window.db_manager.get_product_item(item_id)
                    
                    if not product or not product_item:
                        QMessageBox.warning(self, "Product Not Found", "No product found with the given ID.")
                        return
                    
                    if product_item['status'] == 'sold':
                        QMessageBox.warning(self, "Item Already Sold", "This product item has already been sold.")
                        return
                    
                    # Add to cart
                    self.add_to_cart(product, quantity=1, product_item_id=item_id)
                    
                    # Clear input
                    self.product_id_input.clear()
                    return
                except ValueError:
                    pass
        
        # If not a product item ID, try as regular product ID
        try:
            product_id = int(product_id_text)
            
            # Get product details
            product = self.main_window.db_manager.get_product(product_id)
            
            if not product:
                QMessageBox.warning(self, "Product Not Found", "No product found with the given ID.")
                return
            
            # Add to cart
            self.add_to_cart(product)
            
            # Clear input
            self.product_id_input.clear()
            
        except ValueError:
            QMessageBox.warning(self, "Invalid ID", "Please enter a valid product ID.")
    
    def search_products(self):
        # Get search text
        search_text = self.product_search_input.text().strip().lower()
        
        if not search_text:
            # Clear results if search is empty
            self.product_results.setRowCount(0)
            return
        
        # Search products in database
        products = self.main_window.db_manager.search_products(search_text)
        
        # Display results
        self.product_results.setRowCount(len(products))
        
        for i, product in enumerate(products):
            # Product ID
            id_item = QTableWidgetItem(str(product['id']))
            id_item.setData(Qt.UserRole, product['id'])
            self.product_results.setItem(i, 0, id_item)
            
            # Product Name
            name_item = QTableWidgetItem(product['name'])
            self.product_results.setItem(i, 1, name_item)
            
            # Price - Fix: Use 'selling_price' instead of 'price'
            price_item = QTableWidgetItem(f"£{product['selling_price']:.2f}")
            self.product_results.setItem(i, 2, price_item)
            
            # Stock
            stock_item = QTableWidgetItem(str(product['store_quantity']))
            self.product_results.setItem(i, 3, stock_item)
            
            # Add to cart button
            add_btn = QPushButton("Add to Cart")
            add_btn.setStyleSheet("""
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
            
            # Use lambda with default argument to capture the current product
            add_btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            
            self.product_results.setCellWidget(i, 4, add_btn)
    
    def add_to_cart(self, product, quantity=1, product_item_id=None):
        # Check if we have enough in store
        if not product_item_id and product['store_quantity'] < quantity:
            QMessageBox.warning(
                self, "Insufficient Stock", 
                f"Only {product['store_quantity']} units available in store."
            )
            return
        
        # If it's a serialized product, we need to add each item individually
        # Use get() with default value of False to handle missing 'is_serialized' key
        if product.get('is_serialized', False) and not product_item_id:
            # Get available items
            items = self.main_window.db_manager.get_available_product_items(product['id'])
            
            if not items:
                QMessageBox.warning(self, "No Items Available", "No items available for this product.")
                return
            
            # Add first available item
            product_item_id = items[0]['id']
        
        # Check if product is already in cart
        for item in self.cart_items:
            if item['product_id'] == product['id']:
                # For serialized products, we can't increase quantity
                # Use get() with default value of False to handle missing 'is_serialized' key
                if product.get('is_serialized', False):
                    # Check if this specific item is already in cart
                    if product_item_id and item.get('product_item_id') == product_item_id:
                        QMessageBox.information(
                            self, "Item Already in Cart", 
                            "This specific item is already in your cart."
                        )
                        return
                else:
                    # For non-serialized products, increase quantity
                    if item['quantity'] + quantity > product['store_quantity']:
                        QMessageBox.warning(
                            self, "Quantity Limit", 
                            f"Cannot add more. Only {product['store_quantity']} available in store."
                        )
                        return
                    
                    item['quantity'] += quantity
                    item['total'] = item['price'] * item['quantity']
                    
                    # Update cart display
                    self.update_cart_display()
                    return
        
        # Add new item to cart
        cart_item = {
            'product_id': product['id'],
            'name': product['name'],
            'price': product['selling_price'],  # Use selling_price instead of price
            'quantity': quantity,
            'total': product['selling_price'] * quantity  # Use selling_price instead of price
        }
        
        # Add product item ID if applicable
        if product_item_id:
            cart_item['product_item_id'] = product_item_id
        
        self.cart_items.append(cart_item)
        
        # Update cart display
        self.update_cart_display()
    
    def update_cart_display(self):
        # Update cart table
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            # ID
            id_item = QTableWidgetItem(str(item['product_id']))
            self.cart_table.setItem(row, 0, id_item)
            
            # Name
            name_text = item['name']
            if 'product_item_id' in item:
                name_text += f" (Item #{item['product_item_id']})"  # Add item ID for serialized products
            name_item = QTableWidgetItem(name_text)
            self.cart_table.setItem(row, 1, name_item)
            
            # Price
            price_item = QTableWidgetItem(f"₹{item['price']:.2f}")
            self.cart_table.setItem(row, 2, price_item)
            
            # Quantity
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            qty_layout.setSpacing(5)
            
            # For serialized products, we can't change quantity
            if 'product_item_id' in item:
                qty_label = QLabel(str(item['quantity']))
                qty_label.setAlignment(Qt.AlignCenter)
                qty_layout.addWidget(qty_label)
            else:
                # Decrease button
                decrease_btn = QPushButton("-")
                decrease_btn.setFixedSize(25, 25)
                decrease_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                decrease_btn.clicked.connect(lambda checked, r=row: self.decrease_quantity(r))
                
                # Quantity label
                qty_label = QLabel(str(item['quantity']))
                qty_label.setAlignment(Qt.AlignCenter)
                qty_label.setFixedWidth(30)
                
                # Increase button
                increase_btn = QPushButton("+")
                increase_btn.setFixedSize(25, 25)
                increase_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
                increase_btn.clicked.connect(lambda checked, r=row: self.increase_quantity(r))
                
                qty_layout.addWidget(decrease_btn)
                qty_layout.addWidget(qty_label)
                qty_layout.addWidget(increase_btn)
            
            self.cart_table.setCellWidget(row, 3, qty_widget)
            
            # Total
            total_item = QTableWidgetItem(f"₹{item['total']:.2f}")
            self.cart_table.setItem(row, 4, total_item)
            
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
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            
            self.cart_table.setCellWidget(row, 5, remove_btn)
        
        # Update cart summary
        self.update_cart_summary()
    
    def decrease_quantity(self, row):
        if row < 0 or row >= len(self.cart_items):
            return
        
        # Get cart item
        cart_item = self.cart_items[row]
        
        # Decrease quantity
        if cart_item['quantity'] > 1:
            cart_item['quantity'] -= 1
            cart_item['total'] = cart_item['price'] * cart_item['quantity']
            
            # Update cart display
            self.update_cart_display()
    
    def increase_quantity(self, row):
        if row < 0 or row >= len(self.cart_items):
            return
        
        # Get cart item
        cart_item = self.cart_items[row]
        
        # Check if we have enough in store
        product = self.main_window.db_manager.get_product(cart_item['product_id'])
        
        if cart_item['quantity'] >= product['store_quantity']:
            QMessageBox.warning(
                self, "Quantity Limit", 
                f"Cannot add more. Only {product['store_quantity']} available in store."
            )
            return
        
        # Increase quantity
        cart_item['quantity'] += 1
        cart_item['total'] = cart_item['price'] * cart_item['quantity']
        
        # Update cart display
        self.update_cart_display()
    
    def remove_from_cart(self, row):
        if row < 0 or row >= len(self.cart_items):
            return
        
        # Remove item from cart
        self.cart_items.pop(row)
        
        # Update cart display
        self.update_cart_display()
    
    def clear_cart(self):
        # Confirm with user
        reply = QMessageBox.question(
            self, "Clear Cart", 
            "Are you sure you want to clear the cart?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear cart
            self.cart_items = []
            
            # Update cart display
            self.update_cart_display()
    
    def update_cart_summary(self):
        # Calculate cart summary
        total_items = sum(item['quantity'] for item in self.cart_items)
        subtotal = sum(item['total'] for item in self.cart_items)
        
        # Apply discount
        discount_percent = self.discount_input.value()
        discount_amount = subtotal * (discount_percent / 100)
        
        # Calculate total
        total = subtotal - discount_amount
        
        # Apply GST if selected
        if self.include_gst_checkbox.isChecked():
            gst_amount = total * 0.18  # 18% GST
            total += gst_amount
        
        # Update labels
        self.items_count_label.setText(f"Items: {total_items}")
        self.subtotal_label.setText(f"Subtotal: ₹{subtotal:.2f}")
        self.discount_label.setText(f"Discount: ₹{discount_amount:.2f}")
        self.total_label.setText(f"Total: ₹{total:.2f}")
    
    def load_customers_for_completer(self):
        # Get all customers from database
        customers = self.main_window.db_manager.get_all_customers()
        print(f"DEBUG: Retrieved {len(customers)} customers from database")
        
        # Clear current model
        self.customer_completer_model.clear()
        
        # Add customers to model
        for customer in customers:
            display_text = f"{customer['id']} - {customer['name']} - {customer['phone']}"  # Format: ID - Name - Phone
            item = QStandardItem(display_text)
            item.setData(customer['id'], Qt.UserRole)  # Store customer ID as user data
            self.customer_completer_model.appendRow(item)
            print(f"DEBUG: Added customer to model: {display_text}, ID: {customer['id']}")
        
        # Make sure the completer is using the updated model
        completer = self.customer_search_input.completer()
        completer.setModel(self.customer_completer_model)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setMaxVisibleItems(10)
        
        # Force UI update
        QApplication.processEvents()
        
        print(f"DEBUG: Completer model now has {self.customer_completer_model.rowCount()} items")
        
        # If we have customers but the model is empty, try again after a delay
        if len(customers) > 0 and self.customer_completer_model.rowCount() == 0:
            print("DEBUG: Model is empty despite having customers, scheduling reload")
            QTimer.singleShot(500, self.load_customers_for_completer)
    
    def search_customers(self):
        # Get search text
        search_text = self.customer_search_input.text().strip().lower()
        
        # If search text is empty, load all customers
        if not search_text:
            self.load_customers_for_completer()
            # Show the completer popup with all customers
            if self.customer_search_input.hasFocus():
                self.customer_search_input.completer().complete()
            return
        
        # If search text is too short, don't search yet
        if len(search_text) < 2:
            return
        
        # Search customers in database
        customers = self.main_window.db_manager.search_customers(search_text)
        
        # Clear current model
        self.customer_completer_model.clear()
        
        # Add customers to model
        for customer in customers:
            display_text = f"{customer['id']} - {customer['name']} - {customer['phone']}"  # Format: ID - Name - Phone
            item = QStandardItem(display_text)
            item.setData(customer['id'], Qt.UserRole)  # Store customer ID as user data
            self.customer_completer_model.appendRow(item)
            
        print(f"DEBUG: Added {len(customers)} customers to completer model")
        print(f"DEBUG: Model now has {self.customer_completer_model.rowCount()} items")
        
        # Make sure the completer is using the updated model
        self.customer_search_input.completer().setModel(self.customer_completer_model)
        
        # Show completer popup if we have results
        if customers and self.customer_search_input.hasFocus():
            self.customer_search_input.completer().complete()
    
    def select_customer_from_completer(self, text):
        print(f"DEBUG: select_customer_from_completer called with text: '{text}'")
        print(f"DEBUG: Model has {self.customer_completer_model.rowCount()} items")
        
        if not text or not text.strip():
            print("DEBUG: Empty text provided")
            return
        
        # Try to extract customer ID from the text (format: "ID - Name - Phone")
        try:
            # First, check if the text starts with a number followed by ' - '
            parts = text.split(' - ')
            if len(parts) >= 2 and parts[0].isdigit():
                customer_id = int(parts[0])
                print(f"DEBUG: Extracted customer_id from text: {customer_id}")
                success = self.load_customer(customer_id)
                if success:
                    # Clear the search input after successful load
                    QTimer.singleShot(1000, self.customer_search_input.clear)
                    return True
        except Exception as e:
            print(f"DEBUG: Error extracting customer ID: {str(e)}")
            
        # First try to find an exact match
        for i in range(self.customer_completer_model.rowCount()):
            item = self.customer_completer_model.item(i)
            if item and item.text() == text:
                customer_id = item.data(Qt.UserRole)
                print(f"DEBUG: Found exact match, customer_id: {customer_id}")
                if customer_id:
                    success = self.load_customer(customer_id)
                    if success:
                        # Clear the search input after successful load
                        QTimer.singleShot(1000, self.customer_search_input.clear)
                        return True
        
        # If we get here, we didn't find an exact match
        # Try to find a partial match (e.g., if user typed part of a name)
        search_text = text.lower()
        for i in range(self.customer_completer_model.rowCount()):
            item = self.customer_completer_model.item(i)
            if item and search_text in item.text().lower():
                customer_id = item.data(Qt.UserRole)
                print(f"DEBUG: Found partial match, customer_id: {customer_id}")
                if customer_id:
                    success = self.load_customer(customer_id)
                    if success:
                        QTimer.singleShot(1000, self.customer_search_input.clear)
                        return True
                
        # If we still haven't found a match, try to match just the beginning of each item
        for i in range(self.customer_completer_model.rowCount()):
            item = self.customer_completer_model.item(i)
            if item and item.text().lower().startswith(search_text):
                customer_id = item.data(Qt.UserRole)
                print(f"DEBUG: Found startswith match, customer_id: {customer_id}")
                if customer_id:
                    success = self.load_customer(customer_id)
                    if success:
                        QTimer.singleShot(1000, self.customer_search_input.clear)
                        return True
        
        print(f"DEBUG: No match found for text: '{text}'")
        return False
    
    def on_customer_highlighted(self, text):
        """Called when a customer is highlighted in the completer popup"""
        # Store the highlighted text for potential selection
        self.highlighted_customer_text = text
    
    def on_search_return_pressed(self):
        """Called when return key is pressed in the search input"""
        search_text = self.customer_search_input.text().strip()
        if search_text:
            # Try to select the customer based on the current text
            self.select_customer_from_completer(search_text)
        elif hasattr(self, 'highlighted_customer_text') and self.highlighted_customer_text:
            # If no text but we have a highlighted item, use that
            self.select_customer_from_completer(self.highlighted_customer_text)
    def load_customer(self, customer_id):
        """Load customer data and display it"""
        print(f"DEBUG: Loading customer with ID: {customer_id}")
        
        # Get customer data from database - use get_customer_by_id for more details
        customer = self.main_window.db_manager.get_customer_by_id(customer_id)
        
        if not customer:
            print(f"DEBUG: Customer not found with ID: {customer_id}")
            return False
            
        print(f"DEBUG: Customer data retrieved: {customer}")
        
        # Store customer data
        self.customer = customer
        
        # Update customer details display
        self.update_customer_display()
        
        return True
        
    def update_customer_display(self):
        """Update the customer details display"""
        if not self.customer:
            self.customer_details_frame.setVisible(False)
            return
            
        # Show customer details frame
        self.customer_details_frame.setVisible(True)
        
        # Clear existing widgets
        for i in reversed(range(self.customer_details_layout.count())):
            widget = self.customer_details_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # Create HTML content for customer details
        html_content = f"""
        <div style='font-family: Arial; padding: 10px;'>
            <h3 style='margin: 0 0 10px 0; color: #2c3e50;'>{self.customer['name']}</h3>
            <p style='margin: 5px 0; color: #7f8c8d;'><b>Phone:</b> {self.customer['phone']}</p>
        """
        
        if self.customer.get('email'):
            html_content += f"<p style='margin: 5px 0; color: #7f8c8d;'><b>Email:</b> {self.customer['email']}</p>"
            
        if self.customer.get('address'):
            html_content += f"<p style='margin: 5px 0; color: #7f8c8d;'><b>Address:</b> {self.customer['address']}</p>"
            
        if self.customer.get('gst_number'):
            html_content += f"<p style='margin: 5px 0; color: #7f8c8d;'><b>GST:</b> {self.customer['gst_number']}</p>"
            
        html_content += "</div>"
        
        # Create label with HTML content
        details_label = QLabel()
        details_label.setTextFormat(Qt.RichText)
        details_label.setText(html_content)
        details_label.setStyleSheet("background-color: white; border-radius: 4px; padding: 5px;")
        
        # Add to layout
        self.customer_details_layout.addWidget(details_label)
        
        # Force UI update
        QApplication.processEvents()
    
    def on_completer_activated_index(self, index):
        """Called when a completer item is activated by index (direct click)"""
        if index.isValid():
            model = index.model()
            text = model.data(index, Qt.DisplayRole)
            customer_id = model.data(index, Qt.UserRole)
            print(f"DEBUG: Completer activated by index - text: '{text}', customer_id: {customer_id}")
            if customer_id:
                success = self.load_customer(customer_id)
                print(f"DEBUG: load_customer result: {success}")
                if success:
                    # Update the search input with the selected customer text
                    self.customer_search_input.setText(text)
                    # Then clear it after a delay
                    QTimer.singleShot(1000, self.customer_search_input.clear)
    
    def on_editing_finished(self):
        """Called when editing is finished in the search input"""
        search_text = self.customer_search_input.text().strip()
        if search_text:
            # Try to auto-select if there's an exact match
            self.select_customer_from_completer(search_text)
    
    def load_customer(self, customer_id):
        print(f"DEBUG: load_customer called with customer_id: {customer_id}")
        
        try:
            # Get customer from database
            customer = self.main_window.db_manager.get_customer(customer_id)
            
            if not customer:
                print(f"DEBUG: No customer found for ID: {customer_id}")
                return False
            
            print(f"DEBUG: Customer loaded: {customer}")
            
            # Store customer
            self.customer = customer
            
            # Update customer details display with better formatting
            self.customer_name_label.setText(f"<b>Name:</b> {customer['name']}")
            self.customer_phone_label.setText(f"<b>Phone:</b> {customer['phone']}")
            self.customer_email_label.setText(f"<b>Email:</b> {customer['email'] or 'N/A'}")
            self.customer_address_label.setText(f"<b>Address:</b> {customer['address'] or 'N/A'}")
            
            # Make sure labels are visible and styled
            for label in [self.customer_name_label, self.customer_phone_label, 
                         self.customer_email_label, self.customer_address_label]:
                label.setVisible(True)
                label.setStyleSheet("color: #2c3e50; font-size: 12px; padding: 2px;")
            
            # Show customer details frame
            self.customer_details_frame.setVisible(True)
            print(f"DEBUG: Customer details frame made visible")
            
            # Force multiple UI updates to ensure visibility
            self.customer_details_frame.repaint()
            self.customer_details_frame.update()
            self.update()
            
            # Process events to ensure UI updates
            QApplication.processEvents()
            
            print(f"DEBUG: Customer details should now be visible")
            return True
            
        except Exception as e:
            print(f"DEBUG: Error loading customer: {e}")
            return False
    
    def clear_customer(self):
        # Clear customer
        self.customer = None
        
        # Hide customer details frame
        self.customer_details_frame.setVisible(False)
        
        # Clear customer search input
        self.customer_search_input.clear()
    
    # refresh_data method is already defined at the top of the class
    
    def show_new_customer_dialog(self):
        # Show dialog to add new customer
        dialog = CustomerDialog(self, self.main_window)
        
        if dialog.exec_() == QDialog.Accepted:
            # Reload customers for completer
            self.load_customers_for_completer()
            
            # Load the newly added customer
            if dialog.customer_id:
                self.load_customer(dialog.customer_id)
    
    def complete_sale(self):
        # Check if cart is empty
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add items to the cart before completing the sale.")
            return
        
        # Check if customer is selected
        if not self.customer:
            # Ask if user wants to continue without customer
            reply = QMessageBox.question(
                self, "No Customer Selected", 
                "No customer is selected. Do you want to add a customer before completing the sale?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Show dialog to add new customer
                dialog = CustomerDialog(self, self.main_window)
                if dialog.exec_() == QDialog.Accepted and dialog.customer_id:
                    self.load_customer(dialog.customer_id)
                else:
                    # If dialog was cancelled or no customer was added, return to the sale screen
                    return
            elif reply == QMessageBox.Cancel:
                return
        
        # Collect sale data
        sale_data = {
            'customer_id': self.customer['id'] if self.customer else None,
            'total_amount': sum(item['total'] for item in self.cart_items),
            'discount_amount': sum(item['total'] for item in self.cart_items) * (self.discount_input.value() / 100),
            'tax_amount': sum(item['total'] for item in self.cart_items) * 0.18 if self.include_gst_checkbox.isChecked() else 0,
            'final_amount': sum(item['total'] for item in self.cart_items) * (1 - self.discount_input.value() / 100) * (1.18 if self.include_gst_checkbox.isChecked() else 1),
            'payment_method': self.payment_method_combo.currentText(),
            'include_gst': self.include_gst_checkbox.isChecked(),
            'created_by': self.main_window.current_user['id'] if hasattr(self.main_window, 'current_user') and self.main_window.current_user else None
        }
        
        # Prepare sale items for database
        sale_items = []
        for item in self.cart_items:
            sale_items.append({
                'product_id': item['product_id'],
                'product_item_id': item.get('product_item_id'),
                'quantity': item['quantity'],
                'unit_price': item['price'],
                'discount_percentage': self.discount_input.value(),
                'total_price': item['total']
            })
        
        # Create sale in database
        result = self.main_window.db_manager.create_sale(sale_data, sale_items)
        
        if not result:
            QMessageBox.critical(self, "Error", "Failed to create sale. Please try again.")
            return
        
        sale_id, invoice_number = result
        
        # Show success message
        QMessageBox.information(
            self, "Sale Complete", 
            f"Sale #{sale_id} completed successfully. Invoice has been generated."
        )
        
        # Generate and show invoice
        self.main_window.show_invoice_generator(sale_id)
        
        # Clear cart and customer
        self.cart_items = []
        self.update_cart_display()
        self.clear_customer()
        self.discount_input.setValue(0)

class CustomerDialog(QDialog):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.customer_id = None
        
        self.setWindowTitle("Add New Customer")
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumWidth(400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter customer name")
        form_layout.addRow("Name:", self.name_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address (optional)")
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter address (optional)")
        form_layout.addRow("Address:", self.address_input)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addSpacing(20)
        main_layout.addWidget(button_box)
    
    def accept(self):
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Customer name is required.")
            return
        
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Phone number is required.")
            return
        
        # Collect customer data
        customer_data = {
            'name': self.name_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'address': self.address_input.text().strip()
        }
        
        # Add customer to database
        self.customer_id = self.main_window.db_manager.add_customer(customer_data)
        
        if not self.customer_id:
            QMessageBox.critical(self, "Error", "Failed to add customer. Please try again.")
            return
        
        super().accept()