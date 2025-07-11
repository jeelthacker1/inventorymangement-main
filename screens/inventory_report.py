import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QDateEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QDialog, 
                             QFormLayout, QGroupBox, QTextEdit, QFrame, QSplitter,
                             QTabWidget, QCalendarWidget, QCheckBox, QSpinBox, 
                             QFileDialog, QProgressBar)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QPainter, QTextDocument
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class InventoryReportScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_inventory_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title and back button
        title_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        title_layout.addWidget(back_btn)
        
        title_label = QLabel("Inventory Report")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Export buttons
        export_pdf_btn = QPushButton("Export PDF")
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        export_pdf_btn.clicked.connect(self.export_pdf)
        title_layout.addWidget(export_pdf_btn)
        
        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_csv_btn.clicked.connect(self.export_csv)
        title_layout.addWidget(export_csv_btn)
        
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
        
        # Category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        # Categories will be populated from database
        category_layout.addWidget(self.category_filter)
        
        filter_layout.addLayout(category_layout)
        
        # Stock level filter
        stock_level_layout = QHBoxLayout()
        stock_level_layout.addWidget(QLabel("Stock Level:"))
        
        self.stock_level_filter = QComboBox()
        self.stock_level_filter.addItems(["All", "Low Stock", "Out of Stock", "In Stock"])
        stock_level_layout.addWidget(self.stock_level_filter)
        
        filter_layout.addLayout(stock_level_layout)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by product name or ID")
        search_layout.addWidget(self.search_input)
        
        filter_layout.addLayout(search_layout)
        
        # Apply filter button
        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        apply_filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_filter_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
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
        
        # Table view tab
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Product Name", "Category", "Cost Price", "Selling Price", 
            "Store Qty", "Warehouse Qty", "Total Value"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        table_layout.addWidget(self.inventory_table)
        
        # Chart view tab
        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)
        
        chart_splitter = QSplitter(Qt.Vertical)
        
        # Category distribution chart
        category_group = QGroupBox("Inventory by Category")
        category_layout = QVBoxLayout(category_group)
        
        self.category_figure = Figure(figsize=(8, 4), dpi=100)
        self.category_canvas = FigureCanvas(self.category_figure)
        category_layout.addWidget(self.category_canvas)
        
        chart_splitter.addWidget(category_group)
        
        # Value distribution chart
        value_group = QGroupBox("Inventory Value Distribution")
        value_layout = QVBoxLayout(value_group)
        
        self.value_figure = Figure(figsize=(8, 4), dpi=100)
        self.value_canvas = FigureCanvas(self.value_figure)
        value_layout.addWidget(self.value_canvas)
        
        chart_splitter.addWidget(value_group)
        
        chart_layout.addWidget(chart_splitter)
        
        # Add tabs
        self.tabs.addTab(table_tab, "Table View")
        self.tabs.addTab(chart_tab, "Chart View")
        
        main_layout.addWidget(self.tabs)
        
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
        
        self.total_products_label = QLabel("Total Products: 0")
        summary_layout.addWidget(self.total_products_label)
        
        summary_layout.addStretch()
        
        self.total_value_label = QLabel("Total Inventory Value: ₹0.00")
        self.total_value_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        summary_layout.addWidget(self.total_value_label)
        
        summary_layout.addStretch()
        
        self.low_stock_label = QLabel("Low Stock Items: 0")
        self.low_stock_label.setStyleSheet("color: #e74c3c;")
        summary_layout.addWidget(self.low_stock_label)
        
        main_layout.addWidget(summary_frame)
    
    def load_inventory_data(self):
        # Get all products from database
        products = self.main_window.db_manager.get_all_products()
        
        # Populate category filter
        self.populate_category_filter(products)
        
        # Apply any filters
        self.apply_filters()
    
    def populate_category_filter(self, products):
        # Get unique categories
        categories = set()
        for product in products:
            if product['category'] and product['category'].strip():
                categories.add(product['category'])
        
        # Clear and repopulate category filter
        current_category = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        
        for category in sorted(categories):
            self.category_filter.addItem(category)
        
        # Restore previous selection if possible
        index = self.category_filter.findText(current_category)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
    
    def apply_filters(self):
        # Get all products
        products = self.main_window.db_manager.get_all_products()
        
        # Apply category filter
        category = self.category_filter.currentText()
        if category != "All Categories":
            products = [p for p in products if p['category'] == category]
        
        # Apply stock level filter
        stock_level = self.stock_level_filter.currentText()
        if stock_level == "Low Stock":
            products = [p for p in products if (p['store_quantity'] + p['warehouse_quantity']) < p['min_stock_level']]
        elif stock_level == "Out of Stock":
            products = [p for p in products if (p['store_quantity'] + p['warehouse_quantity']) == 0]
        elif stock_level == "In Stock":
            products = [p for p in products if (p['store_quantity'] + p['warehouse_quantity']) > 0]
        
        # Apply search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            products = [p for p in products if 
                       search_text in str(p['id']).lower() or 
                       search_text in p['name'].lower()]
        
        # Update table
        self.update_inventory_table(products)
        
        # Update charts
        self.update_charts(products)
        
        # Update summary
        self.update_summary(products)
    
    def update_inventory_table(self, products):
        self.inventory_table.setRowCount(0)
        
        for row, product in enumerate(products):
            self.inventory_table.insertRow(row)
            
            # ID
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            
            # Product Name
            self.inventory_table.setItem(row, 1, QTableWidgetItem(product['name']))
            
            # Category
            self.inventory_table.setItem(row, 2, QTableWidgetItem(product['category'] or ""))
            
            # Cost Price
            cost_price_item = QTableWidgetItem(f"₹{product['cost_price']:.2f}")
            cost_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.inventory_table.setItem(row, 3, cost_price_item)
            
            # Selling Price
            selling_price_item = QTableWidgetItem(f"₹{product['selling_price']:.2f}")
            selling_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.inventory_table.setItem(row, 4, selling_price_item)
            
            # Store Quantity
            store_qty_item = QTableWidgetItem(str(product['store_quantity']))
            store_qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.inventory_table.setItem(row, 5, store_qty_item)
            
            # Warehouse Quantity
            warehouse_qty_item = QTableWidgetItem(str(product['warehouse_quantity']))
            warehouse_qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.inventory_table.setItem(row, 6, warehouse_qty_item)
            
            # Total Value
            total_qty = product['store_quantity'] + product['warehouse_quantity']
            total_value = total_qty * product['cost_price']
            total_value_item = QTableWidgetItem(f"₹{total_value:.2f}")
            total_value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.inventory_table.setItem(row, 7, total_value_item)
            
            # Highlight low stock items
            if total_qty < product['min_stock_level']:
                for col in range(self.inventory_table.columnCount()):
                    self.inventory_table.item(row, col).setBackground(Qt.red)
                    self.inventory_table.item(row, col).setForeground(Qt.white)
    
    def update_charts(self, products):
        # Category distribution chart
        self.category_figure.clear()
        ax1 = self.category_figure.add_subplot(111)
        
        # Group by category
        category_data = {}
        for product in products:
            category = product['category'] or "Uncategorized"
            if category not in category_data:
                category_data[category] = 0
            category_data[category] += product['store_quantity'] + product['warehouse_quantity']
        
        # Sort by quantity
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        categories = [item[0] for item in sorted_categories]
        quantities = [item[1] for item in sorted_categories]
        
        # Create bar chart
        bars = ax1.bar(categories, quantities, color='#3498db')
        ax1.set_xlabel('Category')
        ax1.set_ylabel('Quantity')
        ax1.set_title('Inventory Quantity by Category')
        
        # Rotate x-axis labels if there are many categories
        if len(categories) > 5:
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Add quantity labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        self.category_figure.tight_layout()
        self.category_canvas.draw()
        
        # Value distribution chart
        self.value_figure.clear()
        ax2 = self.value_figure.add_subplot(111)
        
        # Group by category for value
        value_data = {}
        for product in products:
            category = product['category'] or "Uncategorized"
            if category not in value_data:
                value_data[category] = 0
            value_data[category] += (product['store_quantity'] + product['warehouse_quantity']) * product['cost_price']
        
        # Sort by value
        sorted_value_categories = sorted(value_data.items(), key=lambda x: x[1], reverse=True)
        value_categories = [item[0] for item in sorted_value_categories]
        values = [item[1] for item in sorted_value_categories]
        
        # Create pie chart
        wedges, texts, autotexts = ax2.pie(
            values, 
            labels=value_categories,
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Paired(range(len(value_categories)))
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax2.axis('equal')  
        ax2.set_title('Inventory Value Distribution by Category')
        
        # Make text more readable
        for text in texts + autotexts:
            text.set_fontsize(9)
        
        self.value_figure.tight_layout()
        self.value_canvas.draw()
    
    def update_summary(self, products):
        # Total products
        self.total_products_label.setText(f"Total Products: {len(products)}")
        
        # Total value
        total_value = sum((p['store_quantity'] + p['warehouse_quantity']) * p['cost_price'] for p in products)
        self.total_value_label.setText(f"Total Inventory Value: ₹{total_value:.2f}")
        
        # Low stock items
        low_stock_count = sum(1 for p in products if (p['store_quantity'] + p['warehouse_quantity']) < p['min_stock_level'])
        self.low_stock_label.setText(f"Low Stock Items: {low_stock_count}")
    
    def export_pdf(self):
        # Ask for file location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Inventory Report", "", "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        if not file_path.endswith('.pdf'):
            file_path += '.pdf'
        
        try:
            # Create printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPrinter.A4)
            
            # Create HTML document
            doc = QTextDocument()
            html = self.generate_report_html()
            doc.setHtml(html)
            
            # Print to PDF
            doc.print_(printer)
            
            QMessageBox.information(self, "Export Successful", 
                                   f"Inventory report exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                               f"Failed to export report: {str(e)}")
    
    def export_csv(self):
        # Ask for file location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Inventory Report", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        if not file_path.endswith('.csv'):
            file_path += '.csv'
        
        try:
            # Get filtered products
            products = []
            for row in range(self.inventory_table.rowCount()):
                product = {
                    'id': self.inventory_table.item(row, 0).text(),
                    'name': self.inventory_table.item(row, 1).text(),
                    'category': self.inventory_table.item(row, 2).text(),
                    'cost_price': self.inventory_table.item(row, 3).text().replace('₹', ''),
                    'selling_price': self.inventory_table.item(row, 4).text().replace('₹', ''),
                    'store_quantity': self.inventory_table.item(row, 5).text(),
                    'warehouse_quantity': self.inventory_table.item(row, 6).text(),
                    'total_value': self.inventory_table.item(row, 7).text().replace('₹', '')
                }
                products.append(product)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['id', 'name', 'category', 'cost_price', 'selling_price', 
                             'store_quantity', 'warehouse_quantity', 'total_value']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for product in products:
                    writer.writerow(product)
            
            QMessageBox.information(self, "Export Successful", 
                                   f"Inventory report exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                               f"Failed to export report: {str(e)}")
    
    def generate_report_html(self):
        # Get current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Get summary data
        total_products = self.inventory_table.rowCount()
        total_value = self.total_value_label.text().replace("Total Inventory Value: ", "")
        low_stock = self.low_stock_label.text().replace("Low Stock Items: ", "")
        
        # Start HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                .summary {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                .summary-item {{ margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .low-stock {{ background-color: #ffcccc; }}
                .text-right {{ text-align: right; }}
            </style>
        </head>
        <body>
            <h1>Inventory Report</h1>
            
            <div class="header">
                <div>Generated on: {current_date}</div>
            </div>
            
            <div class="summary">
                <div class="summary-item"><strong>Total Products:</strong> {total_products}</div>
                <div class="summary-item"><strong>Total Inventory Value:</strong> {total_value}</div>
                <div class="summary-item"><strong>Low Stock Items:</strong> {low_stock}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Product Name</th>
                        <th>Category</th>
                        <th class="text-right">Cost Price</th>
                        <th class="text-right">Selling Price</th>
                        <th class="text-right">Store Qty</th>
                        <th class="text-right">Warehouse Qty</th>
                        <th class="text-right">Total Value</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add table rows
        for row in range(self.inventory_table.rowCount()):
            product_id = self.inventory_table.item(row, 0).text()
            name = self.inventory_table.item(row, 1).text()
            category = self.inventory_table.item(row, 2).text()
            cost_price = self.inventory_table.item(row, 3).text()
            selling_price = self.inventory_table.item(row, 4).text()
            store_qty = self.inventory_table.item(row, 5).text()
            warehouse_qty = self.inventory_table.item(row, 6).text()
            total_value = self.inventory_table.item(row, 7).text()
            
            # Check if this is a low stock item
            is_low_stock = False
            for col in range(self.inventory_table.columnCount()):
                if self.inventory_table.item(row, col).background() == Qt.red:
                    is_low_stock = True
                    break
            
            row_class = "low-stock" if is_low_stock else ""
            
            html += f"""
                <tr class="{row_class}">
                    <td>{product_id}</td>
                    <td>{name}</td>
                    <td>{category}</td>
                    <td class="text-right">{cost_price}</td>
                    <td class="text-right">{selling_price}</td>
                    <td class="text-right">{store_qty}</td>
                    <td class="text-right">{warehouse_qty}</td>
                    <td class="text-right">{total_value}</td>
                </tr>
            """
        
        # Close HTML
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def go_back(self):
        """Return to the previous screen"""
        self.main_window.show_admin_dashboard()