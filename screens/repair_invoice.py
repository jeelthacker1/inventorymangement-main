import os
import datetime
print("Repair Invoice module loaded successfully")
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QScrollArea, QCheckBox, QDateEdit, QLineEdit, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QFileDialog)
from PyQt5.QtCore import Qt, QDate, QSizeF
from PyQt5.QtGui import QFont, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

class RepairInvoiceScreen(QWidget):
    def __init__(self, main_window, repair_id):
        super().__init__()
        self.main_window = main_window
        self.repair_id = repair_id
        
        # Initialize variables
        self.customer_data = None
        self.repair_data = None
        self.invoice_items = []
        self.invoice_date = QDate.currentDate().toString('yyyy-MM-dd')
        self.invoice_number = self.generate_invoice_number()
        
        # Initialize UI
        self.init_ui()
        
        # Load repair data
        self.load_repair_data()
    
    def generate_invoice_number(self):
        # Get the current date
        today = datetime.datetime.today()
        year = today.year
        month = today.month
        day = today.day
        
        # Get the count of invoices for today
        count = self.main_window.db_manager.get_invoice_count_for_date(today.strftime('%Y-%m-%d'))
        
        # Format: INV-YYYYMMDD-XXX where XXX is a sequential number
        return f"INV-{year}{month:02d}{day:02d}-{count+1:03d}"
    
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
        
        title_label = QLabel("Repair Invoice")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        top_bar_layout.addWidget(back_btn)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        
        # Add print and preview buttons
        preview_btn = QPushButton("Preview Invoice")
        preview_btn.setStyleSheet("""
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
        preview_btn.clicked.connect(self.preview_invoice)
        
        print_btn = QPushButton("Print Invoice")
        print_btn.setStyleSheet("""
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
        print_btn.clicked.connect(self.print_invoice)
        
        save_pdf_btn = QPushButton("Save as PDF")
        save_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        save_pdf_btn.clicked.connect(self.save_as_pdf)
        
        top_bar_layout.addWidget(preview_btn)
        top_bar_layout.addWidget(print_btn)
        top_bar_layout.addWidget(save_pdf_btn)
        
        main_layout.addWidget(top_bar)
        
        # Content area with invoice preview
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Invoice options
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        options_layout = QHBoxLayout(options_frame)
        
        # GST option
        self.include_gst_checkbox = QCheckBox("Include GST (18%)")
        self.include_gst_checkbox.setChecked(True)  # Default to include GST
        self.include_gst_checkbox.stateChanged.connect(self.update_invoice_preview)
        
        # Invoice date
        date_layout = QHBoxLayout()
        date_label = QLabel("Invoice Date:")
        self.invoice_date_edit = QDateEdit()
        self.invoice_date_edit.setCalendarPopup(True)
        self.invoice_date_edit.setDate(QDate.currentDate())
        self.invoice_date_edit.dateChanged.connect(self.update_invoice_date)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.invoice_date_edit)
        
        # Invoice number
        number_layout = QHBoxLayout()
        number_label = QLabel("Invoice Number:")
        self.invoice_number_edit = QLineEdit(self.invoice_number)
        self.invoice_number_edit.setReadOnly(True)  # Make it read-only
        number_layout.addWidget(number_label)
        number_layout.addWidget(self.invoice_number_edit)
        
        options_layout.addWidget(self.include_gst_checkbox)
        options_layout.addStretch()
        options_layout.addLayout(date_layout)
        options_layout.addSpacing(20)
        options_layout.addLayout(number_layout)
        
        content_layout.addWidget(options_frame)
        
        # Invoice preview
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        # Create a scroll area for the invoice preview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # Create the invoice preview widget
        self.invoice_preview = QWidget()
        self.invoice_preview_layout = QVBoxLayout(self.invoice_preview)
        self.invoice_preview_layout.setContentsMargins(20, 20, 20, 20)
        self.invoice_preview_layout.setSpacing(10)
        
        # Set the invoice preview as the scroll area widget
        scroll_area.setWidget(self.invoice_preview)
        preview_layout.addWidget(scroll_area)
        
        content_layout.addWidget(preview_frame)
        
        main_layout.addWidget(content_widget)
    
    def load_repair_data(self):
        # Fetch repair data from database
        self.repair_data = self.main_window.db_manager.get_repair(self.repair_id)
        
        if not self.repair_data:
            QMessageBox.critical(self, "Error", f"Repair with ID {self.repair_id} not found.")
            self.go_back()
            return
            
        # Get customer data
        customer_id = self.repair_data.get('customer_id')
        if customer_id:
            self.customer_data = self.main_window.db_manager.get_customer_by_id(customer_id)
        
        # Get repair items (parts and labor)
        repair_parts = self.main_window.db_manager.get_repair_parts(self.repair_id)
        
        # Clear existing items
        self.invoice_items = []
        
        # Add repair service as an item
        service_charge = float(self.repair_data.get('service_charge', 0))
        if service_charge > 0:
            self.invoice_items.append({
                'name': 'Repair Service',
                'price': service_charge,
                'quantity': 1,
                'discount': 0,
                'total': service_charge
            })
        
        # Add parts as items
        for part in repair_parts:
            part_price = float(part.get('price', 0))
            part_quantity = int(part.get('quantity', 1))
            self.invoice_items.append({
                'name': part.get('name', 'Part'),
                'price': part_price,
                'quantity': part_quantity,
                'discount': 0,
                'total': part_price * part_quantity
            })
            
        # Update the invoice preview
        self.update_invoice_preview()
    
    def update_invoice_date(self):
        self.invoice_date = self.invoice_date_edit.date().toString('yyyy-MM-dd')
        self.update_invoice_preview()
    
    def update_invoice_preview(self):
        # Check if invoice_preview_layout exists
        if not hasattr(self, 'invoice_preview_layout'):
            print("Warning: invoice_preview_layout not found in update_invoice_preview, initializing UI")
            self.init_ui()
            return
            
        # Clear the current preview
        for i in reversed(range(self.invoice_preview_layout.count())): 
            widget = self.invoice_preview_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Shop information - Header
        shop_info_layout = QVBoxLayout()
        
        # Shop name in large font
        shop_name = QLabel("K BICYCLE")
        shop_name.setStyleSheet("font-size: 28px; font-weight: bold; color: #000000; text-align: center;")
        shop_name.setAlignment(Qt.AlignCenter)
        shop_info_layout.addWidget(shop_name)
        
        # Shop address
        shop_address = QLabel("SHOP NO 1/2, TRUST MARBLE COMPLEX, MADHAPAR (370020)")
        shop_address.setStyleSheet("font-size: 12px; color: #333333; text-align: center;")
        shop_address.setAlignment(Qt.AlignCenter)
        shop_info_layout.addWidget(shop_address)
        
        # Shop contact
        shop_contact = QLabel("BHUJ, KUTCH | GSTN: 24ABTPK4541R1ZB")
        shop_contact.setStyleSheet("font-size: 12px; color: #333333; text-align: center;")
        shop_contact.setAlignment(Qt.AlignCenter)
        shop_info_layout.addWidget(shop_contact)
        
        self.invoice_preview_layout.addLayout(shop_info_layout)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #cccccc;")
        self.invoice_preview_layout.addWidget(separator)
        
        # Tax Invoice Header
        tax_invoice_label = QLabel("REPAIR INVOICE")
        tax_invoice_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000; text-align: center;")
        tax_invoice_label.setAlignment(Qt.AlignCenter)
        self.invoice_preview_layout.addWidget(tax_invoice_label)
        
        # Memo details (Invoice number, date, etc.)
        memo_details = QHBoxLayout()
        
        # Left side - Customer details
        memo_left = QVBoxLayout()
        
        memo_left_label = QLabel("Customer Details:")
        memo_left_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        memo_left.addWidget(memo_left_label)
        
        # Customer name
        customer_name = "Walk-in Customer"
        if self.customer_data and self.customer_data.get('name'):
            customer_name = self.customer_data['name']
        memo_left_name = QLabel(f"Name: {customer_name}")
        memo_left_name.setStyleSheet("font-weight: bold;")
        memo_left.addWidget(memo_left_name)
        
        # Customer mobile
        customer_mobile = "-"
        if self.customer_data and self.customer_data.get('phone'):
            customer_mobile = self.customer_data['phone']
        memo_left_mobile = QLabel(f"Mobile: {customer_mobile}")
        memo_left.addWidget(memo_left_mobile)
        
        # Customer GSTN (if available)
        customer_gstn = "-"
        if self.customer_data and self.customer_data.get('gst_number'):
            customer_gstn = self.customer_data['gst_number']
        memo_left_gstn = QLabel(f"GSTN: {customer_gstn}")
        memo_left.addWidget(memo_left_gstn)
        
        # Customer address
        customer_address = "-"
        if self.customer_data and self.customer_data.get('address'):
            customer_address = self.customer_data['address']
        memo_left_address = QLabel(f"Address: {customer_address}")
        memo_left.addWidget(memo_left_address)
        
        # Right side - Invoice details
        memo_right = QVBoxLayout()
        
        memo_right_label = QLabel("Invoice Details:")
        memo_right_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        memo_right.addWidget(memo_right_label)
        
        # Add invoice details
        memo_right_invoice = QLabel(f"Invoice #: {self.invoice_number}")
        memo_right_invoice.setStyleSheet("font-weight: bold;")
        memo_right.addWidget(memo_right_invoice)
        
        memo_right_date = QLabel(f"Date: {self.invoice_date}")
        memo_right.addWidget(memo_right_date)
        
        # Add repair details
        if hasattr(self, 'repair_data') and self.repair_data:
            memo_right_repair = QLabel(f"Repair ID: {self.repair_id}")
            memo_right.addWidget(memo_right_repair)
            
            device = self.repair_data.get('device', '-')
            memo_right_device = QLabel(f"Device: {device}")
            memo_right.addWidget(memo_right_device)
            
            serial_number = self.repair_data.get('serial_number', '-')
            if serial_number:
                memo_right_serial = QLabel(f"Serial: {serial_number}")
                memo_right.addWidget(memo_right_serial)
            
            issue = self.repair_data.get('issue', '-')
            if issue:
                memo_right_issue = QLabel(f"Issue: {issue}")
                memo_right.addWidget(memo_right_issue)
        
        memo_details.addLayout(memo_left)
        memo_details.addLayout(memo_right)
        
        self.invoice_preview_layout.addLayout(memo_details)
        
        # Add a separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #cccccc;")
        self.invoice_preview_layout.addWidget(separator2)
        
        # Items table
        items_table = QTableWidget()
        items_table.setColumnCount(6)
        items_table.setHorizontalHeaderLabels(["#", "Item", "Qty", "Rate", "GST", "Amount"])
        items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        items_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #e0e0e0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        
        # Add items to the table
        subtotal = 0
        total_tax = 0
        include_gst = self.include_gst_checkbox.isChecked()
        
        items_table.setRowCount(len(self.invoice_items))
        
        for row, item in enumerate(self.invoice_items):
            # Item number
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            items_table.setItem(row, 0, num_item)
            
            # Item name
            name_item = QTableWidgetItem(item['name'])
            items_table.setItem(row, 1, name_item)
            
            # Quantity
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setTextAlignment(Qt.AlignCenter)
            items_table.setItem(row, 2, qty_item)
            
            # Rate
            rate_item = QTableWidgetItem(f"₹{item['price']:.2f}")
            rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            items_table.setItem(row, 3, rate_item)
            
            # Calculate item price (without GST)
            item_price = item['price'] * item['quantity']
            subtotal += item_price
            
            # Calculate GST amount if included
            gst_amount = 0
            if include_gst:
                # GST is 18% of the price
                gst_amount = item_price * 0.18
                total_tax += gst_amount
                gst_item = QTableWidgetItem(f"₹{gst_amount:.2f}")
            else:
                gst_item = QTableWidgetItem("-")
            gst_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            items_table.setItem(row, 4, gst_item)
            
            # Total amount for this item
            item_total = item_price + gst_amount if include_gst else item_price
            amount_item = QTableWidgetItem(f"₹{item_total:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            items_table.setItem(row, 5, amount_item)
        
        self.invoice_preview_layout.addWidget(items_table)
        
        # Totals section
        totals_layout = QVBoxLayout()
        
        # Subtotal
        subtotal_layout = QHBoxLayout()
        subtotal_layout.addStretch()
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setStyleSheet("font-weight: bold;")
        subtotal_value = QLabel(f"₹{subtotal:.2f}")
        subtotal_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        subtotal_value.setMinimumWidth(100)
        subtotal_layout.addWidget(subtotal_label)
        subtotal_layout.addWidget(subtotal_value)
        totals_layout.addLayout(subtotal_layout)
        
        # GST
        if include_gst:
            # CGST (9%)
            cgst_layout = QHBoxLayout()
            cgst_layout.addStretch()
            cgst_label = QLabel("CGST (9%):")
            cgst_label.setStyleSheet("font-weight: bold;")
            cgst_value = QLabel(f"₹{total_tax/2:.2f}")
            cgst_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cgst_value.setMinimumWidth(100)
            cgst_layout.addWidget(cgst_label)
            cgst_layout.addWidget(cgst_value)
            totals_layout.addLayout(cgst_layout)
            
            # SGST (9%)
            sgst_layout = QHBoxLayout()
            sgst_layout.addStretch()
            sgst_label = QLabel("SGST (9%):")
            sgst_label.setStyleSheet("font-weight: bold;")
            sgst_value = QLabel(f"₹{total_tax/2:.2f}")
            sgst_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            sgst_value.setMinimumWidth(100)
            sgst_layout.addWidget(sgst_label)
            sgst_layout.addWidget(sgst_value)
            totals_layout.addLayout(sgst_layout)
        
        # Total
        total_amount = subtotal + total_tax
        
        # Round to nearest whole number
        rounded_total = round(total_amount)
        round_off = rounded_total - total_amount
        
        # Round off amount
        round_off_layout = QHBoxLayout()
        round_off_layout.addStretch()
        round_off_label = QLabel("Round Off:")
        round_off_label.setStyleSheet("font-weight: bold;")
        round_off_value = QLabel(f"₹{round_off:.2f}")
        round_off_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        round_off_value.setMinimumWidth(100)
        round_off_layout.addWidget(round_off_label)
        round_off_layout.addWidget(round_off_value)
        totals_layout.addLayout(round_off_layout)
        
        # Grand Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_label = QLabel("Grand Total:")
        total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        total_value = QLabel(f"₹{rounded_total:.2f}")
        total_value.setStyleSheet("font-weight: bold; font-size: 16px;")
        total_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_value.setMinimumWidth(100)
        total_layout.addWidget(total_label)
        total_layout.addWidget(total_value)
        totals_layout.addLayout(total_layout)
        
        # Amount in words
        amount_words_layout = QHBoxLayout()
        amount_words_layout.addStretch()
        amount_words_label = QLabel("Amount in Words:")
        amount_words_label.setStyleSheet("font-weight: bold;")
        amount_words_value = QLabel(f"{self.number_to_words(rounded_total)} Rupees Only")
        amount_words_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amount_words_layout.addWidget(amount_words_label)
        amount_words_layout.addWidget(amount_words_value)
        totals_layout.addLayout(amount_words_layout)
        
        self.invoice_preview_layout.addLayout(totals_layout)
        
        # Payment method and status
        if self.repair_data and 'payment_status' in self.repair_data:
            payment_layout = QHBoxLayout()
            payment_layout.addStretch()
            
            payment_method = self.repair_data.get('payment_method', 'Cash')
            payment_method_label = QLabel(f"Payment Method: {payment_method}")
            payment_method_label.setStyleSheet("font-weight: bold;")
            payment_layout.addWidget(payment_method_label)
            
            payment_layout.addSpacing(20)
            
            payment_status = self.repair_data.get('payment_status', 'Pending')
            payment_status_label = QLabel(f"Status: {payment_status}")
            if payment_status.lower() == 'paid':
                payment_status_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                payment_status_label.setStyleSheet("font-weight: bold; color: red;")
            payment_layout.addWidget(payment_status_label)
            
            self.invoice_preview_layout.addLayout(payment_layout)
        
        # Terms and conditions
        terms_label = QLabel("Terms and Conditions:")
        terms_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        self.invoice_preview_layout.addWidget(terms_label)
        
        terms_text = QLabel("1. All repair work carries a 30-day warranty.\n2. Parts replaced are not returnable.\n3. Payment is due upon completion of repair.\n4. Subject to BHUJ Jurisdiction.")
        terms_text.setWordWrap(True)
        self.invoice_preview_layout.addWidget(terms_text)
        
        # Signature section
        signature_layout = QHBoxLayout()
        
        customer_sign = QVBoxLayout()
        customer_sign_label = QLabel("Customer Signature")
        customer_sign_label.setAlignment(Qt.AlignCenter)
        customer_sign_line = QFrame()
        customer_sign_line.setFrameShape(QFrame.HLine)
        customer_sign_line.setFrameShadow(QFrame.Sunken)
        customer_sign.addStretch()
        customer_sign.addWidget(customer_sign_line)
        customer_sign.addWidget(customer_sign_label)
        
        shop_sign = QVBoxLayout()
        shop_sign_label = QLabel("For, K BICYCLE\nAuthorized Signature")
        shop_sign_label.setAlignment(Qt.AlignCenter)
        shop_sign_line = QFrame()
        shop_sign_line.setFrameShape(QFrame.HLine)
        shop_sign_line.setFrameShadow(QFrame.Sunken)
        shop_sign.addStretch()
        shop_sign.addWidget(shop_sign_line)
        shop_sign.addWidget(shop_sign_label)
        
        signature_layout.addLayout(customer_sign)
        signature_layout.addSpacing(50)
        signature_layout.addLayout(shop_sign)
        
        self.invoice_preview_layout.addLayout(signature_layout)
    
    def get_invoice_html(self):
        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in self.invoice_items)
        include_gst = self.include_gst_checkbox.isChecked()
        total_tax = subtotal * 0.18 if include_gst else 0
        total_amount = subtotal + total_tax
        
        # Round to nearest whole number
        rounded_total = round(total_amount)
        round_off = rounded_total - total_amount
        
        # Create HTML content
        html = """
        <div class="invoice-container">
            <div class="header">
                <div class="shop-name">K BICYCLE</div>
                <div class="shop-address">SHOP NO 1/2, TRUST MARBLE COMPLEX, MADHAPAR (370020)</div>
                <div class="shop-contact">BHUJ, KUTCH | GSTN: 24ABTPK4541R1ZB</div>
            </div>
            
            <div class="separator"></div>
            
            <div class="invoice-title">REPAIR INVOICE</div>
            
            <div class="info-section">
                <div class="customer-info">
                    <div class="section-title">Customer Details:</div>
        """
        
        # Customer details
        customer_name = "Walk-in Customer"
        customer_mobile = "-"
        customer_gstn = "-"
        customer_address = "-"
        
        if self.customer_data:
            if self.customer_data.get('name'):
                customer_name = self.customer_data['name']
            if self.customer_data.get('phone'):
                customer_mobile = self.customer_data['phone']
            if self.customer_data.get('gst_number'):
                customer_gstn = self.customer_data['gst_number']
            if self.customer_data.get('address'):
                customer_address = self.customer_data['address']
        
        html += f"""
                    <div class="info-row"><span class="info-label">Name:</span> {customer_name}</div>
                    <div class="info-row"><span class="info-label">Mobile:</span> {customer_mobile}</div>
                    <div class="info-row"><span class="info-label">GSTN:</span> {customer_gstn}</div>
                    <div class="info-row"><span class="info-label">Address:</span> {customer_address}</div>
                </div>
                
                <div class="invoice-info">
                    <div class="section-title">Invoice Details:</div>
                    <div class="info-row"><span class="info-label">Invoice #:</span> {self.invoice_number}</div>
                    <div class="info-row"><span class="info-label">Date:</span> {self.invoice_date}</div>
        """
        
        # Repair details
        if self.repair_data:
            device = self.repair_data.get('device', '-')
            serial_number = self.repair_data.get('serial_number', '-')
            issue = self.repair_data.get('issue', '-')
            
            html += f"""
                    <div class="info-row"><span class="info-label">Repair ID:</span> {self.repair_id}</div>
                    <div class="info-row"><span class="info-label">Device:</span> {device}</div>
            """
            
            if serial_number:
                html += f"""
                    <div class="info-row"><span class="info-label">Serial:</span> {serial_number}</div>
                """
            
            if issue:
                html += f"""
                    <div class="info-row"><span class="info-label">Issue:</span> {issue}</div>
                """
        
        html += """
                </div>
            </div>
            
            <div class="separator"></div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Rate</th>
                        <th>GST</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add items
        for i, item in enumerate(self.invoice_items):
            item_price = item['price'] * item['quantity']
            gst_amount = item_price * 0.18 if include_gst else 0
            item_total = item_price + gst_amount if include_gst else item_price
            
            html += f"""
                    <tr>
                        <td class="text-center">{i+1}</td>
                        <td>{item['name']}</td>
                        <td class="text-center">{item['quantity']}</td>
                        <td class="text-right">₹{item['price']:.2f}</td>
                        <td class="text-right">{f'₹{gst_amount:.2f}' if include_gst else '-'}</td>
                        <td class="text-right">₹{item_total:.2f}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
            
            <div class="totals-section">
        """
        
        # Subtotal
        html += f"""
                <div class="total-row">
                    <div class="total-label">Subtotal:</div>
                    <div class="total-value">₹{subtotal:.2f}</div>
                </div>
        """
        
        # GST
        if include_gst:
            html += f"""
                <div class="total-row">
                    <div class="total-label">CGST (9%):</div>
                    <div class="total-value">₹{total_tax/2:.2f}</div>
                </div>
                <div class="total-row">
                    <div class="total-label">SGST (9%):</div>
                    <div class="total-value">₹{total_tax/2:.2f}</div>
                </div>
            """
        
        # Round off
        html += f"""
                <div class="total-row">
                    <div class="total-label">Round Off:</div>
                    <div class="total-value">₹{round_off:.2f}</div>
                </div>
        """
        
        # Grand total
        html += f"""
                <div class="total-row grand-total">
                    <div class="total-label">Grand Total:</div>
                    <div class="total-value">₹{rounded_total:.2f}</div>
                </div>
                
                <div class="amount-words">
                    Amount in Words: {self.number_to_words(rounded_total)} Rupees Only
                </div>
            </div>
        """
        
        # Payment method and status
        if self.repair_data and 'payment_status' in self.repair_data:
            payment_method = self.repair_data.get('payment_method', 'Cash')
            payment_status = self.repair_data.get('payment_status', 'Pending')
            status_class = "paid" if payment_status.lower() == 'paid' else "pending"
            
            html += f"""
            <div class="payment-info">
                <div class="payment-method">Payment Method: {payment_method}</div>
                <div class="payment-status {status_class}">Status: {payment_status}</div>
            </div>
            """
        
        # Terms and conditions
        html += """
            <div class="terms-section">
                <div class="terms-title">Terms and Conditions:</div>
                <ol class="terms-list">
                    <li>All repair work carries a 30-day warranty.</li>
                    <li>Parts replaced are not returnable.</li>
                    <li>Payment is due upon completion of repair.</li>
                    <li>Subject to BHUJ Jurisdiction.</li>
                </ol>
            </div>
            
            <div class="signature-section">
                <div class="customer-signature">
                    <div class="signature-line"></div>
                    <div class="signature-label">Customer Signature</div>
                </div>
                
                <div class="shop-signature">
                    <div class="signature-line"></div>
                    <div class="signature-label">For, K BICYCLE<br>Authorized Signature</div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def preview_invoice(self):
        # Create a print preview dialog
        preview_dialog = QPrintPreviewDialog()
        preview_dialog.setWindowTitle(f"Invoice Preview - {self.invoice_number}")
        preview_dialog.setMinimumSize(1000, 700)
        
        # Set up the printer
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
        
        # Connect the preview dialog to the print function
        preview_dialog.paintRequested.connect(lambda printer: self.print_html_to_printer(printer))
        
        # Show the preview dialog
        preview_dialog.exec_()
    
    def print_invoice(self):
        # Set up the printer
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
        
        # Show print dialog
        print_dialog = QPrintDialog(printer)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            self.print_html_to_printer(printer)
    
    def save_as_pdf(self):
        try:
            # Create default directory if it doesn't exist
            invoice_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "invoice")
            
            if not os.path.exists(invoice_dir):
                try:
                    os.makedirs(invoice_dir)
                except Exception as dir_error:
                    print(f"Error creating invoice directory: {str(dir_error)}")
                    # If we can't create the directory, use the desktop as fallback
                    invoice_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
            
            # Default file path
            default_path = os.path.join(invoice_dir, f"{self.invoice_number}.pdf")
            
            # Ask for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice as PDF",
                default_path,
                "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return
            
            # Ensure the file has .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # Set up the PDF writer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
            
            # Print to PDF
            result = self.print_html_to_printer(printer)
            
            if not result:
                QMessageBox.warning(self, "PDF Generation Failed", "Failed to create the PDF file. Please try again.")
                return
            
            # Verify the file was created
            if os.path.exists(file_path):
                QMessageBox.information(self, "PDF Saved", f"Invoice has been saved as PDF to:\n{file_path}")
                
                # Ask if user wants to open the PDF
                reply = QMessageBox.question(self, "Open PDF", "Do you want to open the PDF now?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    # Open the PDF with the default application
                    import subprocess
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                    elif os.name == 'posix':  # macOS or Linux
                        subprocess.call(('xdg-open', file_path))
            else:
                QMessageBox.warning(self, "PDF Generation Failed", "Failed to create the PDF file. Please try again.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred while saving the PDF:\n{str(e)}")
    
    def print_html_to_printer(self, printer):
        try:
            # Create a document to render the HTML
            document = QTextDocument()
            
            # Get the HTML content
            html_content = self.get_invoice_html()
            
            # Add CSS styles for printing
            html_with_styles = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                    .invoice-container {{ width: 100%; padding: 20px; }}
                    .header {{ text-align: center; margin-bottom: 20px; }}
                    .shop-name {{ font-size: 24pt; font-weight: bold; margin-bottom: 5px; }}
                    .shop-address {{ font-size: 10pt; margin-bottom: 2px; }}
                    .shop-contact {{ font-size: 10pt; }}
                    .separator {{ border-top: 1px solid #000; margin: 10px 0; }}
                    .invoice-title {{ font-size: 16pt; font-weight: bold; text-align: center; margin: 10px 0; }}
                    .info-section {{ display: flex; justify-content: space-between; margin: 15px 0; }}
                    .customer-info, .invoice-info {{ width: 48%; }}
                    .section-title {{ font-weight: bold; font-size: 12pt; margin-bottom: 5px; }}
                    .info-row {{ margin-bottom: 3px; }}
                    .info-label {{ font-weight: bold; }}
                    .items-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                    .items-table th, .items-table td {{ border: 1px solid #000; padding: 5px; }}
                    .items-table th {{ background-color: #f0f0f0; font-weight: bold; }}
                    .text-center {{ text-align: center; }}
                    .text-right {{ text-align: right; }}
                    .totals-section {{ margin-top: 10px; }}
                    .total-row {{ display: flex; justify-content: flex-end; margin: 3px 0; }}
                    .total-label {{ font-weight: bold; width: 150px; text-align: right; padding-right: 10px; }}
                    .total-value {{ width: 100px; text-align: right; }}
                    .grand-total {{ font-weight: bold; font-size: 14pt; margin-top: 5px; }}
                    .amount-words {{ text-align: right; margin-top: 10px; font-style: italic; }}
                    .payment-info {{ display: flex; justify-content: flex-end; margin: 10px 0; }}
                    .payment-method {{ margin-right: 20px; font-weight: bold; }}
                    .payment-status {{ font-weight: bold; }}
                    .paid {{ color: green; }}
                    .pending {{ color: red; }}
                    .terms-section {{ margin-top: 20px; }}
                    .terms-title {{ font-weight: bold; margin-bottom: 5px; }}
                    .terms-list {{ margin-top: 5px; padding-left: 20px; }}
                    .terms-list li {{ margin-bottom: 3px; }}
                    .signature-section {{ display: flex; justify-content: space-between; margin-top: 40px; }}
                    .customer-signature, .shop-signature {{ width: 45%; text-align: center; }}
                    .signature-line {{ border-top: 1px solid #000; margin-bottom: 5px; }}
                    .signature-label {{ font-size: 10pt; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            document.setHtml(html_with_styles)
            
            # Set the document size to match the printer page size with proper margins
            page_size = printer.pageRect().size()
            # Use 85% of page size to ensure proper margins and prevent cutoff
            doc_width = page_size.width() * 0.85
            doc_height = page_size.height() * 0.85
            document.setPageSize(QSizeF(doc_width, doc_height))
            
            # Print the document
            document.print_(printer)
            
            return True
        except Exception as e:
            print(f"Error printing HTML to printer: {str(e)}")
            QMessageBox.critical(self, "Printing Error", f"An error occurred while generating the document:\n{str(e)}")
            return False
    
    def go_back(self):
        # Check if user is admin or employee and return to the appropriate dashboard
        if self.main_window.current_user_role == 'admin':
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()
    
    def number_to_words(self, number):
        # Convert number to Indian Rupees in words
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        def convert_below_thousand(n):
            if n < 20:
                return ones[n]
            elif n < 100:
                return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
            else:
                return ones[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' ' + convert_below_thousand(n % 100))
        
        if number == 0:
            return 'Zero'
        
        # Convert to integer
        number = int(number)
        
        result = ''
        
        if number >= 10000000:  # Crore
            result += convert_below_thousand(number // 10000000) + ' Crore '
            number %= 10000000
        
        if number >= 100000:  # Lakh
            result += convert_below_thousand(number // 100000) + ' Lakh '
            number %= 100000
        
        if number >= 1000:  # Thousand
            result += convert_below_thousand(number // 1000) + ' Thousand '
            number %= 1000
        
        if number > 0:
            result += convert_below_thousand(number)
        
        return result.strip()