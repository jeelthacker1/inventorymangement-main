import os
import datetime
import qrcode
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QLineEdit,
                             QComboBox, QDoubleSpinBox, QSpinBox, QTabWidget,
                             QFormLayout, QDialogButtonBox, QFileDialog,
                             QScrollArea, QGroupBox, QCheckBox, QRadioButton,
                             QButtonGroup, QDateEdit, QTextEdit, QCompleter,
                             QCalendarWidget, QApplication)
from PyQt5.QtCore import Qt, QSize, QSizeF, pyqtSignal, QTimer, QDate, QBuffer, QIODevice
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QStandardItemModel, QStandardItem, QPainter, QPdfWriter, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

class InvoiceScreen(QWidget):
    def __init__(self, main_window, sale_id=None, repair_id=None):
        super().__init__()
        self.main_window = main_window
        self.sale_id = sale_id
        self.repair_id = repair_id
        self.sale_data = None
        self.repair_data = None
        self.customer_data = None
        self.invoice_items = []
        self.invoice_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.invoice_number = self.generate_invoice_number()
        
        # Load data based on what was provided
        if sale_id:
            self.load_sale_data()
        elif repair_id:
            self.load_repair_data()
        
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
        
        title_label = QLabel("Invoice Generator")
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
        
        # Update the invoice preview
        self.update_invoice_preview()
    
    def go_back(self):
        # Check if user is admin or employee and return to the appropriate dashboard
        if self.main_window.current_user_role == 'admin':
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()
    
    def generate_invoice_number(self):
        # Get the current date
        today = datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        
        # Get the count of invoices for today
        count = self.main_window.db_manager.get_invoice_count_for_date(today.strftime('%Y-%m-%d'))
        
        # Format: INV-YYYYMMDD-XXX where XXX is a sequential number
        return f"INV-{year}{month:02d}{day:02d}-{count+1:03d}"
    
    def load_sale_data(self):
        # Load sale data from database
        self.sale_data = self.main_window.db_manager.get_sale(self.sale_id)
        
        if not self.sale_data:
            QMessageBox.critical(self, "Error", "Sale data not found.")
            self.go_back()
            return
        
        # Load customer data
        if self.sale_data['customer_id']:
            self.customer_data = self.main_window.db_manager.get_customer(self.sale_data['customer_id'])
        
        # Load sale items
        sale_items = self.main_window.db_manager.get_sale_items(self.sale_id)
        
        # Convert sale items to invoice items
        self.invoice_items = []
        for item in sale_items:
            invoice_item = {
                'name': item['product_name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'discount': item['discount'],
                'total': item['total']
            }
            self.invoice_items.append(invoice_item)
    
    def load_repair_data(self):
        # Load repair data from database
        self.repair_data = self.main_window.db_manager.get_repair(self.repair_id)
        
        if not self.repair_data:
            QMessageBox.critical(self, "Error", "Repair data not found.")
            self.go_back()
            return
        
        # Load customer data
        if self.repair_data['customer_id']:
            self.customer_data = self.main_window.db_manager.get_customer(self.repair_data['customer_id'])
        
        # Load repair parts
        repair_parts = self.main_window.db_manager.get_repair_parts(self.repair_id)
        
        # Convert repair parts to invoice items
        self.invoice_items = []
        
        # Add service charge as an item
        if self.repair_data['service_charge'] > 0:
            service_item = {
                'name': 'Service Charge',
                'quantity': 1,
                'price': self.repair_data['service_charge'],
                'discount': 0,
                'total': self.repair_data['service_charge']
            }
            self.invoice_items.append(service_item)
        
        # Add parts as items
        for part in repair_parts:
            invoice_item = {
                'name': part['product_name'],
                'quantity': part['quantity'],
                'price': part['unit_price'],
                'discount': 0,
                'total': part['total_price']
            }
            self.invoice_items.append(invoice_item)
    
    def update_invoice_date(self):
        self.invoice_date = self.invoice_date_edit.date().toString('yyyy-MM-dd')
        self.update_invoice_preview()
    
    def update_invoice_preview(self):
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
        shop_address.setStyleSheet("font-size: 12px; color: #000000; text-align: center;")
        shop_address.setAlignment(Qt.AlignCenter)
        shop_info_layout.addWidget(shop_address)
        
        # Shop contact
        shop_contact = QLabel("BHUJ, KUTCH")
        shop_contact.setStyleSheet("font-size: 12px; color: #000000; text-align: center;")
        shop_contact.setAlignment(Qt.AlignCenter)
        shop_info_layout.addWidget(shop_contact)
        
        self.invoice_preview_layout.addLayout(shop_info_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #000000;")
        self.invoice_preview_layout.addWidget(separator)
        
        # Tax Invoice Header
        tax_invoice_layout = QHBoxLayout()
        
        # Left side - Memo
        memo_layout = QVBoxLayout()
        memo_label = QLabel("Memo")
        memo_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        memo_layout.addWidget(memo_label)
        
        name_label = QLabel("NAME")
        name_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        memo_layout.addWidget(name_label)
        
        mobil_label = QLabel("MOBIL No.")
        mobil_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        memo_layout.addWidget(mobil_label)
        
        gstn_label = QLabel("GSTN No.")
        gstn_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        memo_layout.addWidget(gstn_label)
        
        add_label = QLabel("ADD.")
        add_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        memo_layout.addWidget(add_label)
        
        # Center - Values
        values_layout = QVBoxLayout()
        values_layout.addWidget(QLabel(":"))
        
        customer_name_value = QLabel(f": {self.customer_data['name'] if self.customer_data else 'SHREE SADGURU ENTERPRISE'}")
        customer_name_value.setStyleSheet("font-size: 12px;")
        values_layout.addWidget(customer_name_value)
        
        mobile_value = QLabel(f": {self.customer_data['phone'] if self.customer_data and self.customer_data['phone'] else '-'}")
        mobile_value.setStyleSheet("font-size: 12px;")
        values_layout.addWidget(mobile_value)
        
        gstn_value = QLabel(f": {self.customer_data['gst_number'] if self.customer_data and self.customer_data.get('gst_number') else '24BBTP1240D1Z3'}")
        gstn_value.setStyleSheet("font-size: 12px;")
        values_layout.addWidget(gstn_value)
        
        address_value = QLabel(f": {self.customer_data['address'] if self.customer_data and self.customer_data['address'] else 'VILA MOTA KANDAGARA, KACHCHH, GUJARAT(370435)'}")
        address_value.setStyleSheet("font-size: 12px;")
        values_layout.addWidget(address_value)
        
        # Right side - Invoice details
        invoice_details_layout = QVBoxLayout()
        
        tax_invoice_label = QLabel("TAX INVOICE")
        tax_invoice_label.setStyleSheet("font-size: 14px; font-weight: bold; text-align: center;")
        tax_invoice_label.setAlignment(Qt.AlignCenter)
        invoice_details_layout.addWidget(tax_invoice_label)
        
        original_label = QLabel("Original")
        original_label.setStyleSheet("font-size: 12px; text-align: center;")
        original_label.setAlignment(Qt.AlignCenter)
        invoice_details_layout.addWidget(original_label)
        
        invoice_number = QLabel(f"Invoice No. {self.invoice_number}")
        invoice_number.setStyleSheet("font-size: 12px; font-weight: bold;")
        invoice_details_layout.addWidget(invoice_number)
        
        invoice_date = QLabel(f"Date : {self.invoice_date}")
        invoice_date.setStyleSheet("font-size: 12px;")
        invoice_details_layout.addWidget(invoice_date)
        
        # Add all layouts to the tax invoice layout
        tax_invoice_layout.addLayout(memo_layout)
        tax_invoice_layout.addLayout(values_layout)
        tax_invoice_layout.addStretch()
        tax_invoice_layout.addLayout(invoice_details_layout)
        
        self.invoice_preview_layout.addLayout(tax_invoice_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        
        self.invoice_preview_layout.addWidget(separator)
        
        # Customer information
        customer_info_layout = QHBoxLayout()
        
        bill_to_layout = QVBoxLayout()
        
        bill_to_label = QLabel("Bill To:")
        bill_to_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        
        customer_name = QLabel(self.customer_data['name'] if self.customer_data else "Walk-in Customer")
        customer_name.setStyleSheet("font-size: 14px; color: #2c3e50;")
        
        customer_phone = QLabel(self.customer_data['phone'] if self.customer_data and self.customer_data['phone'] else "N/A")
        customer_phone.setStyleSheet("font-size: 14px; color: #2c3e50;")
        
        customer_email = QLabel(self.customer_data['email'] if self.customer_data and self.customer_data['email'] else "N/A")
        customer_email.setStyleSheet("font-size: 14px; color: #2c3e50;")
        
        bill_to_layout.addWidget(bill_to_label)
        bill_to_layout.addWidget(customer_name)
        bill_to_layout.addWidget(customer_phone)
        bill_to_layout.addWidget(customer_email)
        
        # For repair invoices, add device information
        if self.repair_data:
            device_info_layout = QVBoxLayout()
            
            device_label = QLabel("Device:")
            device_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
            
            device_name = QLabel(self.repair_data['device'])
            device_name.setStyleSheet("font-size: 14px; color: #2c3e50;")
            
            serial_number = QLabel(f"Serial: {self.repair_data['serial_number'] if self.repair_data['serial_number'] else 'N/A'}")
            serial_number.setStyleSheet("font-size: 14px; color: #2c3e50;")
            
            device_info_layout.addWidget(device_label)
            device_info_layout.addWidget(device_name)
            device_info_layout.addWidget(serial_number)
            
            customer_info_layout.addLayout(bill_to_layout)
            customer_info_layout.addStretch()
            customer_info_layout.addLayout(device_info_layout)
        else:
            customer_info_layout.addLayout(bill_to_layout)
            customer_info_layout.addStretch()
        
        self.invoice_preview_layout.addLayout(customer_info_layout)
        
        # Separator line
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #e0e0e0;")
        
        self.invoice_preview_layout.addWidget(separator2)
        
        # Items table header row
        table_header_layout = QHBoxLayout()
        
        # Create header labels
        sr_header = QLabel("Sr.")
        sr_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        sr_header.setAlignment(Qt.AlignCenter)
        sr_header.setFixedWidth(30)
        
        product_header = QLabel("Product Name")
        product_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        product_header.setAlignment(Qt.AlignCenter)
        
        frame_no_header = QLabel("FRAME NO.")
        frame_no_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        frame_no_header.setAlignment(Qt.AlignCenter)
        frame_no_header.setFixedWidth(100)
        
        qty_header = QLabel("Qty")
        qty_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        qty_header.setAlignment(Qt.AlignCenter)
        qty_header.setFixedWidth(40)
        
        rate_header = QLabel("Rate")
        rate_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        rate_header.setAlignment(Qt.AlignCenter)
        rate_header.setFixedWidth(70)
        
        taxable_header = QLabel("Taxable Amount")
        taxable_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        taxable_header.setAlignment(Qt.AlignCenter)
        taxable_header.setFixedWidth(70)
        
        gst_header = QLabel("GST %")
        gst_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        gst_header.setAlignment(Qt.AlignCenter)
        gst_header.setFixedWidth(50)
        
        tax_amount_header = QLabel("Tax Amount")
        tax_amount_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        tax_amount_header.setAlignment(Qt.AlignCenter)
        tax_amount_header.setFixedWidth(100)
        
        net_amount_header = QLabel("Net Amount")
        net_amount_header.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        net_amount_header.setAlignment(Qt.AlignCenter)
        net_amount_header.setFixedWidth(70)
        
        # Add headers to layout
        table_header_layout.addWidget(sr_header)
        table_header_layout.addWidget(product_header)
        table_header_layout.addWidget(frame_no_header)
        table_header_layout.addWidget(qty_header)
        table_header_layout.addWidget(rate_header)
        table_header_layout.addWidget(taxable_header)
        table_header_layout.addWidget(gst_header)
        table_header_layout.addWidget(tax_amount_header)
        table_header_layout.addWidget(net_amount_header)
        
        self.invoice_preview_layout.addLayout(table_header_layout)
        
        # Calculate subtotal and tax amounts
        subtotal = 0
        total_tax = 0
        
        # Populate items rows
        for row, item in enumerate(self.invoice_items):
            item_row_layout = QHBoxLayout()
            
            # Calculate tax values (assuming 12% GST)
            gst_rate = 12.0
            taxable_amount = item['price']
            tax_amount = (taxable_amount * gst_rate) / 100
            cgst = tax_amount / 2
            sgst = tax_amount / 2
            net_amount = taxable_amount + tax_amount
            
            # Sr. number
            sr_label = QLabel(str(row + 1))
            sr_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            sr_label.setAlignment(Qt.AlignCenter)
            sr_label.setFixedWidth(30)
            
            # Product name
            product_label = QLabel(item['name'])
            product_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            
            # Frame number (using product category or a placeholder)
            frame_no = "N24H029-B94" if row == 0 else "EF5435"
            frame_no_label = QLabel(frame_no)
            frame_no_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            frame_no_label.setAlignment(Qt.AlignCenter)
            frame_no_label.setFixedWidth(100)
            
            # Quantity
            qty_label = QLabel(str(item['quantity']))
            qty_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            qty_label.setAlignment(Qt.AlignCenter)
            qty_label.setFixedWidth(40)
            
            # Rate
            rate_label = QLabel(f"{taxable_amount:.2f}")
            rate_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            rate_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            rate_label.setFixedWidth(70)
            
            # Taxable amount
            taxable_label = QLabel(f"{taxable_amount:.2f}")
            taxable_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            taxable_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            taxable_label.setFixedWidth(70)
            
            # GST %
            gst_label = QLabel(f"{gst_rate:.1f}")
            gst_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            gst_label.setAlignment(Qt.AlignCenter)
            gst_label.setFixedWidth(50)
            
            # Tax amount (CGST + SGST)
            tax_amount_label = QLabel(f"{cgst:.1f}    {sgst:.1f}")
            tax_amount_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            tax_amount_label.setAlignment(Qt.AlignCenter)
            tax_amount_label.setFixedWidth(100)
            
            # Net amount
            net_amount_label = QLabel(f"{net_amount:.1f}")
            net_amount_label.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
            net_amount_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            net_amount_label.setFixedWidth(70)
            
            # Add all widgets to the row layout
            item_row_layout.addWidget(sr_label)
            item_row_layout.addWidget(product_label)
            item_row_layout.addWidget(frame_no_label)
            item_row_layout.addWidget(qty_label)
            item_row_layout.addWidget(rate_label)
            item_row_layout.addWidget(taxable_label)
            item_row_layout.addWidget(gst_label)
            item_row_layout.addWidget(tax_amount_label)
            item_row_layout.addWidget(net_amount_label)
            
            self.invoice_preview_layout.addLayout(item_row_layout)
            
            # Add to totals
            subtotal += taxable_amount
            total_tax += tax_amount
        
        # Add totals row
        totals_row_layout = QHBoxLayout()
        
        # Empty cells for Sr, Product Name, Frame No
        empty_sr = QLabel("")
        empty_sr.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
        empty_sr.setFixedWidth(30)
        
        total_label = QLabel("TOTAL")
        total_label.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        
        empty_frame = QLabel("")
        empty_frame.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
        empty_frame.setFixedWidth(100)
        
        # Total quantity (assuming 2 items)
        total_qty = sum(item['quantity'] for item in self.invoice_items)
        total_qty_label = QLabel(str(total_qty))
        total_qty_label.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        total_qty_label.setAlignment(Qt.AlignCenter)
        total_qty_label.setFixedWidth(40)
        
        # Empty rate cell
        empty_rate = QLabel("")
        empty_rate.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
        empty_rate.setFixedWidth(70)
        
        # Total taxable amount
        total_taxable_label = QLabel(f"{subtotal:.1f}")
        total_taxable_label.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        total_taxable_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_taxable_label.setFixedWidth(70)
        
        # Empty GST cell
        empty_gst = QLabel("")
        empty_gst.setStyleSheet("font-size: 12px; border: 1px solid black; padding: 5px;")
        empty_gst.setFixedWidth(50)
        
        # Total tax amount
        total_tax_label = QLabel(f"{total_tax/2:.1f}    {total_tax/2:.1f}")
        total_tax_label.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        total_tax_label.setAlignment(Qt.AlignCenter)
        total_tax_label.setFixedWidth(100)
        
        # Total net amount
        total_net_amount = subtotal + total_tax
        total_net_label = QLabel(f"{total_net_amount:.1f}")
        total_net_label.setStyleSheet("font-size: 12px; font-weight: bold; border: 1px solid black; padding: 5px;")
        total_net_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_net_label.setFixedWidth(70)
        
        # Add all widgets to the totals row layout
        totals_row_layout.addWidget(empty_sr)
        totals_row_layout.addWidget(total_label)
        totals_row_layout.addWidget(empty_frame)
        totals_row_layout.addWidget(total_qty_label)
        totals_row_layout.addWidget(empty_rate)
        totals_row_layout.addWidget(total_taxable_label)
        totals_row_layout.addWidget(empty_gst)
        totals_row_layout.addWidget(total_tax_label)
        totals_row_layout.addWidget(total_net_label)
        
        self.invoice_preview_layout.addLayout(totals_row_layout)
        
        # Add round off and grand total
        round_off_layout = QHBoxLayout()
        round_off_layout.addStretch()
        
        # GSTN information
        gstn_info = QLabel("GSTN No. 24FCPK3641M2ZB")
        gstn_info.setStyleSheet("font-size: 12px; font-weight: bold;")
        
        # Round off amount
        round_off_label = QLabel("Round off")
        round_off_label.setStyleSheet("font-size: 12px; padding: 5px;")
        round_off_label.setFixedWidth(100)
        
        round_off_amount = QLabel("-0.80")
        round_off_amount.setStyleSheet("font-size: 12px; padding: 5px;")
        round_off_amount.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        round_off_amount.setFixedWidth(70)
        
        round_off_layout.addWidget(gstn_info)
        round_off_layout.addStretch()
        round_off_layout.addWidget(round_off_label)
        round_off_layout.addWidget(round_off_amount)
        
        self.invoice_preview_layout.addLayout(round_off_layout)
        
        # Grand total
        grand_total_layout = QHBoxLayout()
        grand_total_layout.addStretch()
        
        # Bank information
        bank_info_layout = QVBoxLayout()
        bank_name_label = QLabel("Bank Name : HDFC")
        bank_name_label.setStyleSheet("font-size: 12px;")
        bank_acc_label = QLabel("Bank A/c No. : 50200094619383")
        bank_acc_label.setStyleSheet("font-size: 12px;")
        ifsc_label = QLabel("IFSC CODE : HDFC0004302")
        ifsc_label.setStyleSheet("font-size: 12px;")
        
        bank_info_layout.addWidget(bank_name_label)
        bank_info_layout.addWidget(bank_acc_label)
        bank_info_layout.addWidget(ifsc_label)
        
        # Grand total amount
        grand_total_label = QLabel("Grand total")
        grand_total_label.setStyleSheet("font-size: 12px; font-weight: bold; padding: 5px;")
        grand_total_label.setFixedWidth(100)
        
        # Round to nearest whole number
        rounded_total = round(total_net_amount)
        grand_total_amount = QLabel(f"{rounded_total:.2f}")
        grand_total_amount.setStyleSheet("font-size: 12px; font-weight: bold; padding: 5px;")
        grand_total_amount.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grand_total_amount.setFixedWidth(70)
        
        grand_total_layout.addLayout(bank_info_layout)
        grand_total_layout.addStretch()
        grand_total_layout.addWidget(grand_total_label)
        grand_total_layout.addWidget(grand_total_amount)
        
        self.invoice_preview_layout.addLayout(grand_total_layout)
        
        # Remove the reference to items_table that was causing the error
        
        # Add GST breakdown and bill amount in words
        gst_breakdown_layout = QHBoxLayout()
        
        # Total GST text
        total_gst_layout = QVBoxLayout()
        total_gst_text = QLabel("Total GST: One thousand six hundred sixty and eight.")
        total_gst_text.setStyleSheet("font-size: 12px; font-weight: bold;")
        bill_amount_text = QLabel("Bill Amount: Fifteen thousand five hundred.")
        bill_amount_text.setStyleSheet("font-size: 12px; font-weight: bold;")
        
        total_gst_layout.addWidget(total_gst_text)
        total_gst_layout.addWidget(bill_amount_text)
        
        gst_breakdown_layout.addLayout(total_gst_layout)
        gst_breakdown_layout.addStretch()
        
        self.invoice_preview_layout.addLayout(gst_breakdown_layout)
        
        # Terms and conditions
        terms_layout = QVBoxLayout()
        
        terms_header = QLabel("Terms & Condition:")
        terms_header.setStyleSheet("font-size: 12px; font-weight: bold;")
        terms_layout.addWidget(terms_header)
        
        # Add bullet points for terms
        bullet_layout = QVBoxLayout()
        
        terms1 = QLabel("• Goods once sold will not be taken back.")
        terms1.setStyleSheet("font-size: 11px;")
        bullet_layout.addWidget(terms1)
        
        terms2 = QLabel("• Our risk responsibility ceases as soon as the goods leave our premises.")
        terms2.setStyleSheet("font-size: 11px;")
        bullet_layout.addWidget(terms2)
        
        terms3 = QLabel("• Only company warranty will be cover.")
        terms3.setStyleSheet("font-size: 11px;")
        bullet_layout.addWidget(terms3)
        
        terms_layout.addLayout(bullet_layout)
        
        # Add signature section
        signature_layout = QHBoxLayout()
        signature_layout.addStretch()
        
        signature_label = QLabel("(Authorized Signature)")
        signature_label.setStyleSheet("font-size: 12px; margin-top: 50px;")
        signature_layout.addWidget(signature_label)
        
        terms_layout.addLayout(signature_layout)
        
        self.invoice_preview_layout.addLayout(terms_layout)
        
        # GST is already included in our custom invoice layout
        # No need for additional GST calculations here
        
        # Payment information
        payment_info_layout = QHBoxLayout()
        
        payment_method_label = QLabel("Payment Method:")
        payment_method_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        payment_method_value = QLabel()
        if self.sale_data and 'payment_method' in self.sale_data:
            payment_method_value.setText(self.sale_data['payment_method'])
        elif self.repair_data and 'payment_method' in self.repair_data:
            payment_method_value.setText(self.repair_data['payment_method'])
        else:
            payment_method_value.setText("Cash")
        payment_method_value.setStyleSheet("font-size: 14px; color: #2c3e50;")
        
        payment_status_label = QLabel("Payment Status:")
        payment_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        payment_status_value = QLabel()
        if self.sale_data and 'payment_status' in self.sale_data:
            status = self.sale_data['payment_status'].capitalize()
            payment_status_value.setText(status)
            if status == "Paid":
                payment_status_value.setStyleSheet("font-size: 14px; color: #2ecc71;")
            else:
                payment_status_value.setStyleSheet("font-size: 14px; color: #e74c3c;")
        elif self.repair_data and 'payment_status' in self.repair_data:
            status = self.repair_data['payment_status'].capitalize()
            payment_status_value.setText(status)
            if status == "Paid":
                payment_status_value.setStyleSheet("font-size: 14px; color: #2ecc71;")
            else:
                payment_status_value.setStyleSheet("font-size: 14px; color: #e74c3c;")
        else:
            payment_status_value.setText("Paid")
            payment_status_value.setStyleSheet("font-size: 14px; color: #2ecc71;")
        
        payment_info_layout.addWidget(payment_method_label)
        payment_info_layout.addWidget(payment_method_value)
        payment_info_layout.addSpacing(20)
        payment_info_layout.addWidget(payment_status_label)
        payment_info_layout.addWidget(payment_status_value)
        payment_info_layout.addStretch()
        
        self.invoice_preview_layout.addLayout(payment_info_layout)
        
        # Separator line
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.HLine)
        separator3.setFrameShadow(QFrame.Sunken)
        separator3.setStyleSheet("background-color: #e0e0e0;")
        
        self.invoice_preview_layout.addWidget(separator3)
        
        # Notes and terms
        notes_layout = QVBoxLayout()
        
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        notes_value = QLabel("Thank you for your business!")
        notes_value.setStyleSheet("font-size: 14px; color: #2c3e50;")
        notes_value.setWordWrap(True)
        
        terms_label = QLabel("Terms and Conditions:")
        terms_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        terms_value = QLabel("1. All items are non-refundable.\n2. Warranty as per manufacturer's policy.\n3. Repairs have a 30-day warranty on the work performed.")
        terms_value.setStyleSheet("font-size: 14px; color: #2c3e50;")
        terms_value.setWordWrap(True)
        
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(notes_value)
        notes_layout.addSpacing(10)
        notes_layout.addWidget(terms_label)
        notes_layout.addWidget(terms_value)
        
        self.invoice_preview_layout.addLayout(notes_layout)
        
        # Footer
        footer_layout = QHBoxLayout()
        
        footer_text = QLabel("© 2023 Your Shop Name. All rights reserved.")
        footer_text.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        
        footer_layout.addStretch()
        footer_layout.addWidget(footer_text)
        footer_layout.addStretch()
        
        self.invoice_preview_layout.addLayout(footer_layout)
    
    def number_to_words(self, number):
        """Convert a number to words representation for Indian Rupees"""
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_below_thousand(num):
            if num < 20:
                return units[num]
            elif num < 100:
                return tens[num // 10] + (" " + units[num % 10] if num % 10 != 0 else "")
            else:
                return units[num // 100] + " Hundred" + (" " + convert_below_thousand(num % 100) if num % 100 != 0 else "")
        
        if number == 0:
            return "Zero"
        
        # Convert to integer
        number = int(number)
        
        result = ""
        if number >= 10000000:  # Crore
            result += convert_below_thousand(number // 10000000) + " Crore "
            number %= 10000000
        
        if number >= 100000:  # Lakh
            result += convert_below_thousand(number // 100000) + " Lakh "
            number %= 100000
        
        if number >= 1000:  # Thousand
            result += convert_below_thousand(number // 1000) + " Thousand "
            number %= 1000
        
        if number > 0:
            result += convert_below_thousand(number)
        
        return result.strip()
    
    def generate_html_invoice(self):
        # Calculate totals
        subtotal = sum(item['total'] for item in self.invoice_items)
        include_gst = self.include_gst_checkbox.isChecked()
        gst_rate = 12.0  # 12% GST as shown in the invoice image
        gst_amount = subtotal * (gst_rate / 100) if include_gst else 0
        total = subtotal + gst_amount
        
        # Round to nearest whole number for grand total
        rounded_total = round(total)
        round_off = rounded_total - total
        
        # Get payment information
        payment_method = ""
        payment_status = ""
        
        if self.sale_data and 'payment_method' in self.sale_data:
            payment_method = self.sale_data['payment_method']
        elif self.repair_data and 'payment_method' in self.repair_data:
            payment_method = self.repair_data['payment_method']
        else:
            payment_method = "Cash"
        
        if self.sale_data and 'payment_status' in self.sale_data:
            payment_status = self.sale_data['payment_status'].capitalize()
        elif self.repair_data and 'payment_status' in self.repair_data:
            payment_status = self.repair_data['payment_status'].capitalize()
        else:
            payment_status = "Paid"
        
        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Invoice {self.invoice_number}</title>
            <style>
                @page {{ size: A4; margin: 0; }}
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 30px; color: #000; }}
                .invoice-header {{ text-align: center; margin-bottom: 20px; }}
                .shop-name {{ font-size: 42px; font-weight: bold; margin-bottom: 10px; }}
                .shop-address {{ font-size: 16px; margin-bottom: 5px; }}
                .shop-location {{ font-size: 16px; margin-bottom: 15px; }}
                .separator {{ border-top: 3px solid #000; margin: 20px 0; }}
                .tax-invoice-header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                .memo-section {{ width: 40%; }}
                .memo-label {{ font-size: 16px; font-weight: bold; }}
                .memo-value {{ font-size: 16px; margin-left: 5px; }}
                .invoice-info {{ width: 30%; text-align: center; }}
                .tax-invoice-title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .original-label {{ font-size: 16px; margin-bottom: 10px; }}
                .invoice-number {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; }}
                .invoice-date {{ font-size: 16px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
                th, td {{ border: 1px solid black; padding: 10px; font-size: 16px; }}
                th {{ font-weight: bold; text-align: center; background-color: #e0e0e0; }}
                .text-center {{ text-align: center; }}
                .text-right {{ text-align: right; }}
                .totals-section {{ display: flex; justify-content: space-between; margin: 25px 0; }}
                .gstn-info {{ font-size: 16px; font-weight: bold; }}
                .round-off {{ display: flex; justify-content: flex-end; }}
                .round-off-label {{ font-size: 16px; width: 150px; }}
                .round-off-value {{ font-size: 16px; width: 100px; text-align: right; }}
                .bank-info {{ font-size: 16px; margin: 15px 0; }}
                .grand-total {{ display: flex; justify-content: flex-end; font-weight: bold; }}
                .grand-total-label {{ font-size: 20px; width: 150px; }}
                .grand-total-value {{ font-size: 20px; width: 100px; text-align: right; }}
                .gst-breakdown {{ font-size: 18px; font-weight: bold; margin: 20px 0; }}
                .terms-section {{ margin: 30px 0; }}
                .terms-header {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .terms-content {{ font-size: 16px; margin-bottom: 8px; }}
                .signature {{ text-align: right; margin-top: 50px; font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="invoice-header">
                <div class="shop-name">K BICYCLE</div>
                <div class="shop-address">SHOP NO 1/2, TRUST MARBLE COMPLEX, MADHAPAR (370020)</div>
                <div class="shop-location">BHUJ, KUTCH</div>
            </div>
            
            <div class="separator"></div>
            
            <div class="tax-invoice-header">
                <div class="memo-section">
                    <div><span class="memo-label">Memo</span></div>
                    <div><span class="memo-label">NAME</span><span class="memo-value">: {self.customer_data['name'] if self.customer_data else 'SHREE SADGURU ENTERPRISE'}</span></div>
                    <div><span class="memo-label">MOBIL No.</span><span class="memo-value">: {self.customer_data['phone'] if self.customer_data and self.customer_data['phone'] else '-'}</span></div>
                    <div><span class="memo-label">GSTN No.</span><span class="memo-value">: {self.customer_data['gst_number'] if self.customer_data and self.customer_data.get('gst_number') else '24BBTP1240D1Z3'}</span></div>
                    <div><span class="memo-label">ADD.</span><span class="memo-value">: {self.customer_data['address'] if self.customer_data and self.customer_data['address'] else 'VILA MOTA KANDAGARA, KACHCHH, GUJARAT(370435)'}</span></div>
                </div>
                
                <div class="invoice-info">
                    <div class="tax-invoice-title">TAX INVOICE</div>
                    <div class="original-label">Original</div>
                    <div class="invoice-number">Invoice No. {self.invoice_number}</div>
                    <div class="invoice-date">Date: {self.invoice_date}</div>
                </div>
                
                <div></div> <!-- Empty div for spacing -->
            </div>
            
            <div class="separator"></div>
        """
        
        # Add device info for repair invoices
        if self.repair_data:
            html += f"""
                <div class="device-info">
                    <div class="section-title">Device:</div>
                    <div class="customer-details">{self.repair_data['device']}</div>
                    <div class="customer-details">Serial: {self.repair_data['serial_number'] if self.repair_data['serial_number'] else 'N/A'}</div>
                </div>
            """
        
        html += f"""
            </div>
            
            <div class="separator"></div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">Sr.</th>
                        <th style="width: 30%;">Product Name</th>
                        <th style="width: 10%;">FRAME</th>
                        <th style="width: 5%;" class="text-center">Qty</th>
                        <th style="width: 10%;" class="text-right">Rate</th>
                        <th style="width: 10%;" class="text-right">Taxable Amount</th>
                        <th style="width: 5%;" class="text-center">GST %</th>
                        <th style="width: 10%;" class="text-right">Tax Amount</th>
                        <th style="width: 15%;" class="text-right">Net Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add items
        for index, item in enumerate(self.invoice_items, 1):
            # Calculate GST for each item
            taxable_amount = item['total']
            gst_percent = 12.0 if self.include_gst_checkbox.isChecked() else 0
            tax_amount = taxable_amount * (gst_percent / 100)
            net_amount = taxable_amount + tax_amount
            
            # Get frame number if available
            frame_number = item.get('frame_number', '-')
            
            html += f"""
                    <tr>
                        <td class="text-center">{index}</td>
                        <td>{item['name']}</td>
                        <td class="text-center">{frame_number}</td>
                        <td class="text-center">{item['quantity']}</td>
                        <td class="text-right">{item['price']:.2f}</td>
                        <td class="text-right">{taxable_amount:.2f}</td>
                        <td class="text-center">{gst_percent:.1f}</td>
                        <td class="text-right">{tax_amount:.2f}</td>
                        <td class="text-right">{net_amount:.2f}</td>
                    </tr>
            """
        
        html += f"""
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="3" class="text-right">TOTAL</td>
                        <td class="text-center">{sum(item['quantity'] for item in self.invoice_items)}</td>
                        <td></td>
                        <td class="text-right">{subtotal:.2f}</td>
                        <td></td>
                        <td class="text-right">{gst_amount:.2f}</td>
                        <td class="text-right">{total:.2f}</td>
                    </tr>
                </tfoot>
            </table>
            
            <div class="totals-section">
                <div class="gstn-info">
                    GSTN No. 24ABTPK4541R1ZB
                </div>
                <div>
                    <div class="round-off">
                        <div class="round-off-label">Round Off</div>
                        <div class="round-off-value">{round_off:.2f}</div>
                    </div>
                    <div class="grand-total">
                        <div class="grand-total-label">Grand Total</div>
                        <div class="grand-total-value">₹{rounded_total:.2f}</div>
                    </div>
                </div>
            </div>
            
            <div class="gst-breakdown">
                Amt (Rupees {self.number_to_words(rounded_total)} Only)
            </div>
        """
        
        html += f"""
            <div class="bank-info">
                <div>Bank Details: HDFC BANK</div>
                <div>A/C No.: 50200012345678</div>
                <div>IFSC Code: HDFC0001234</div>
            </div>
            
            <div class="terms-section">
                <div class="terms-header">Terms & Condition:</div>
                <div class="terms-content">• Goods once sold will not be taken back.</div>
                <div class="terms-content">• Our responsibility ceases as soon as the goods leave our premises.</div>
                <div class="terms-content">• Subject to BHUJ Jurisdiction.</div>
            </div>
            
            <div class="signature">
                For, K BICYCLE<br>
                Authorized Signatory
            </div>
        </body>
        </html>
        """
        
        return html
    
    def preview_invoice(self):
        # Generate HTML invoice
        html = self.generate_html_invoice()
        
        # Create a preview dialog
        preview_dialog = QPrintPreviewDialog()
        preview_dialog.setWindowTitle(f"Invoice Preview - {self.invoice_number}")
        preview_dialog.setMinimumSize(1000, 700)
        
        # Set up the printer
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
        
        # Connect the preview dialog to the print function
        preview_dialog.paintRequested.connect(lambda printer: self.print_html_to_printer(html, printer))
        
        # Show the preview dialog
        preview_dialog.exec_()
    
    def print_invoice(self):
        # Generate HTML invoice
        html = self.generate_html_invoice()
        
        # Set up the printer
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
        
        # Show print dialog
        print_dialog = QPrintDialog(printer)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            self.print_html_to_printer(html, printer)
    
    def save_as_pdf(self):
        print("Starting PDF generation process...")
        # Generate HTML invoice
        html = self.generate_html_invoice()
        
        try:
            # Create default directory if it doesn't exist
            invoice_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "invoice")
            print(f"Invoice directory path: {invoice_dir}")
            
            if not os.path.exists(invoice_dir):
                print(f"Creating invoice directory: {invoice_dir}")
                try:
                    os.makedirs(invoice_dir)
                    print(f"Successfully created invoice directory: {invoice_dir}")
                except Exception as dir_error:
                    print(f"Error creating invoice directory: {str(dir_error)}")
                    # If we can't create the directory, use the desktop as fallback
                    invoice_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
                    print(f"Using fallback directory: {invoice_dir}")
            
            # Default file path
            default_path = os.path.join(invoice_dir, f"{self.invoice_number}.pdf")
            print(f"Default save path: {default_path}")
            
            # Ask for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice as PDF",
                default_path,
                "PDF Files (*.pdf)"
            )
            
            if not file_path:
                print("User cancelled the save dialog")
                return
            
            print(f"Selected save path: {file_path}")
            
            # Ensure the file has .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
                print(f"Added .pdf extension: {file_path}")
            
            # Set up the PDF writer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
            
            print("Printing HTML to PDF...")
            # Print to PDF
            result = self.print_html_to_printer(html, printer)
            
            if not result:
                print("PDF generation failed in print_html_to_printer method")
                QMessageBox.warning(self, "PDF Generation Failed", "Failed to create the PDF file. Please try again.")
                return
            
            # Verify the file was created
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"PDF file created successfully: {file_path} (Size: {file_size} bytes)")
                
                QMessageBox.information(self, "PDF Saved", f"Invoice has been saved as PDF to:\n{file_path}")
                
                # Ask if user wants to open the PDF
                reply = QMessageBox.question(self, "Open PDF", "Do you want to open the PDF now?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    print(f"Opening PDF file: {file_path}")
                    # Open the PDF with the default application
                    import subprocess
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                    elif os.name == 'posix':  # macOS or Linux
                        subprocess.call(('xdg-open', file_path))
            else:
                print(f"PDF file not found after generation: {file_path}")
                QMessageBox.warning(self, "PDF Generation Failed", "Failed to create the PDF file. Please try again.")
        except Exception as e:
            print(f"PDF generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred while saving the PDF:\n{str(e)}")
            print(f"PDF generation error: {str(e)}")
    
    def print_html_to_printer(self, html, printer):
        try:
            # Create a document to render the HTML
            document = QTextDocument()
            
            # Set a much larger default font before setting HTML
            font = QFont("Arial", 16)  # Use Arial font with 16pt size (larger)
            document.setDefaultFont(font)
            
            # Modify HTML to ensure much larger font sizes
            html_with_styles = f"""
            <html>
            <head>
            <style>
            body {{ 
                font-family: Arial, sans-serif; 
                font-size: 16pt; 
                margin: 30px; 
                line-height: 1.4;
            }}
            h1 {{ 
                font-size: 24pt; 
                font-weight: bold; 
                margin-bottom: 15px; 
                text-align: center;
            }}
            h2 {{ 
                font-size: 20pt; 
                font-weight: bold; 
                margin-bottom: 12px; 
            }}
            h3 {{ 
                font-size: 18pt; 
                font-weight: bold; 
                margin-bottom: 10px; 
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 15px 0; 
            }}
            th, td {{ 
                padding: 12px; 
                border: 2px solid #000; 
                font-size: 14pt; 
                text-align: left;
            }}
            th {{ 
                background-color: #f0f0f0; 
                font-weight: bold; 
                font-size: 15pt;
            }}
            .header {{ 
                font-size: 18pt; 
                margin-bottom: 20px; 
                font-weight: bold;
            }}
            .total {{ 
                font-weight: bold; 
                font-size: 16pt; 
                background-color: #f9f9f9;
            }}
            .company-info {{ 
                font-size: 14pt; 
                margin-bottom: 20px;
            }}
            .invoice-details {{ 
                font-size: 14pt; 
                margin: 15px 0;
            }}
            </style>
            </head>
            <body>
            {html}
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
            
            print("Document successfully printed to printer/PDF")
            return True
        except Exception as e:
            print(f"Error printing HTML to printer: {str(e)}")
            QMessageBox.critical(self, "Printing Error", f"An error occurred while generating the document:\n{str(e)}")
            return False

class RepairInvoiceScreen(InvoiceScreen):
    def __init__(self, main_window, repair_id):
        super().__init__(main_window, repair_id=repair_id)

class SaleInvoiceScreen(InvoiceScreen):
    def __init__(self, main_window, sale_id):
        super().__init__(main_window, sale_id=sale_id)