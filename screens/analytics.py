import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSpacerItem,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QComboBox, QDateEdit,
                             QTabWidget, QFormLayout, QGroupBox, QRadioButton,
                             QButtonGroup, QFileDialog, QDialog, QLineEdit,
                             QDoubleSpinBox, QSpinBox, QCheckBox)
from PyQt5.QtCore import Qt, QSize, QTimer, QDate
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter

class AnalyticsScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
        # Set up a timer to refresh data every 5 minutes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # 300,000 ms = 5 minutes
    
    def go_back(self):
        """Return to the previous screen"""
        self.main_window.show_admin_dashboard()
    
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
        
        title_label = QLabel("Analytics Dashboard")
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
        
        # Content area with tabs
        content_area = QWidget()
        content_area.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Date filter
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
        
        # Period selection for trend analysis
        period_label = QLabel("Period:")
        period_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.period_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }
        """)
        self.period_combo.currentIndexChanged.connect(self.refresh_data)
        
        # Export button
        export_btn = QPushButton("Export Data")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        export_btn.clicked.connect(self.export_data)
        
        date_filter_layout.addWidget(date_filter_label)
        date_filter_layout.addWidget(self.date_range_combo)
        date_filter_layout.addWidget(self.start_date)
        date_filter_layout.addWidget(date_separator)
        date_filter_layout.addWidget(self.end_date)
        date_filter_layout.addStretch()
        date_filter_layout.addWidget(period_label)
        date_filter_layout.addWidget(self.period_combo)
        date_filter_layout.addWidget(export_btn)
        
        content_layout.addWidget(date_filter_frame)
        
        # Create tabs for different analytics views
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
        
        # Sales Analysis Tab
        sales_tab = QWidget()
        sales_layout = QVBoxLayout(sales_tab)
        
        # Sales trend chart
        self.sales_figure = Figure(figsize=(10, 6), dpi=100)
        self.sales_canvas = FigureCanvas(self.sales_figure)
        self.sales_canvas.setMinimumHeight(300)
        sales_layout.addWidget(self.sales_canvas)
        
        # Sales metrics
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        metrics_layout = QHBoxLayout(metrics_frame)
        
        self.create_metric_widget(metrics_layout, "Total Sales", "₹0.00", "total_sales", "#3498db")
        self.create_metric_widget(metrics_layout, "Average Sale", "₹0.00", "avg_sale", "#9b59b6")
        self.create_metric_widget(metrics_layout, "Number of Sales", "0", "num_sales", "#2ecc71")
        self.create_metric_widget(metrics_layout, "Items Sold", "0", "items_sold", "#f39c12")
        
        sales_layout.addWidget(metrics_frame)
        
        # Sales by payment method
        payment_frame = QFrame()
        payment_layout = QHBoxLayout(payment_frame)
        
        # Payment method chart
        self.payment_figure = Figure(figsize=(5, 4), dpi=100)
        self.payment_canvas = FigureCanvas(self.payment_figure)
        payment_layout.addWidget(self.payment_canvas)
        
        # Sales by category chart
        self.category_figure = Figure(figsize=(5, 4), dpi=100)
        self.category_canvas = FigureCanvas(self.category_figure)
        payment_layout.addWidget(self.category_canvas)
        
        sales_layout.addWidget(payment_frame)
        
        # Product Analysis Tab
        product_tab = QWidget()
        product_layout = QVBoxLayout(product_tab)
        
        # Top products chart
        self.product_figure = Figure(figsize=(10, 6), dpi=100)
        self.product_canvas = FigureCanvas(self.product_figure)
        self.product_canvas.setMinimumHeight(300)
        product_layout.addWidget(self.product_canvas)
        
        # Product tables frame
        product_tables_frame = QFrame()
        product_tables_layout = QHBoxLayout(product_tables_frame)
        
        # Top selling products table
        top_products_group = QGroupBox("Top Selling Products")
        top_products_layout = QVBoxLayout(top_products_group)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(5)
        self.top_products_table.setHorizontalHeaderLabels(["Product", "Category", "Quantity", "Revenue", "% of Sales"])
        self.top_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_products_table.setAlternatingRowColors(True)
        self.top_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        top_products_layout.addWidget(self.top_products_table)
        product_tables_layout.addWidget(top_products_group)
        
        # Non-selling products table
        non_selling_group = QGroupBox("Non-Selling Products")
        non_selling_layout = QVBoxLayout(non_selling_group)
        
        self.non_selling_table = QTableWidget()
        self.non_selling_table.setColumnCount(4)
        self.non_selling_table.setHorizontalHeaderLabels(["Product", "Category", "Store Qty", "Last Updated"])
        self.non_selling_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.non_selling_table.setAlternatingRowColors(True)
        self.non_selling_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        non_selling_layout.addWidget(self.non_selling_table)
        product_tables_layout.addWidget(non_selling_group)
        
        product_layout.addWidget(product_tables_frame)
        
        # Profit Analysis Tab
        profit_tab = QWidget()
        profit_layout = QVBoxLayout(profit_tab)
        
        # Profit metrics
        profit_metrics_frame = QFrame()
        profit_metrics_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        profit_metrics_layout = QHBoxLayout(profit_metrics_frame)
        
        self.create_metric_widget(profit_metrics_layout, "Gross Profit", "₹0.00", "gross_profit", "#2ecc71")
        self.create_metric_widget(profit_metrics_layout, "Net Profit", "₹0.00", "net_profit", "#3498db")
        self.create_metric_widget(profit_metrics_layout, "Gross Margin", "0%", "gross_margin", "#9b59b6")
        self.create_metric_widget(profit_metrics_layout, "Net Margin", "0%", "net_margin", "#f39c12")
        
        profit_layout.addWidget(profit_metrics_frame)
        
        # Profit charts frame
        profit_charts_frame = QFrame()
        profit_charts_layout = QHBoxLayout(profit_charts_frame)
        
        # Revenue vs Cost chart
        self.profit_figure = Figure(figsize=(5, 4), dpi=100)
        self.profit_canvas = FigureCanvas(self.profit_figure)
        profit_charts_layout.addWidget(self.profit_canvas)
        
        # Expense breakdown chart
        self.expense_figure = Figure(figsize=(5, 4), dpi=100)
        self.expense_canvas = FigureCanvas(self.expense_figure)
        profit_charts_layout.addWidget(self.expense_canvas)
        
        profit_layout.addWidget(profit_charts_frame)
        
        # Expenses table
        expenses_group = QGroupBox("Recent Expenses")
        expenses_layout = QVBoxLayout(expenses_group)
        
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(5)
        self.expenses_table.setHorizontalHeaderLabels(["Date", "Category", "Description", "Amount", "Created By"])
        self.expenses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expenses_table.setAlternatingRowColors(True)
        self.expenses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        expenses_layout.addWidget(self.expenses_table)
        profit_layout.addWidget(expenses_group)
        
        # Inventory Analysis Tab
        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(inventory_tab)
        
        # Inventory metrics
        inventory_metrics_frame = QFrame()
        inventory_metrics_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        inventory_metrics_layout = QHBoxLayout(inventory_metrics_frame)
        
        self.create_metric_widget(inventory_metrics_layout, "Total Products", "0", "total_products", "#3498db")
        self.create_metric_widget(inventory_metrics_layout, "Store Items", "0", "store_items", "#2ecc71")
        self.create_metric_widget(inventory_metrics_layout, "Warehouse Items", "0", "warehouse_items", "#9b59b6")
        self.create_metric_widget(inventory_metrics_layout, "Low Stock Items", "0", "low_stock", "#e74c3c")
        
        inventory_layout.addWidget(inventory_metrics_frame)
        
        # Inventory charts frame
        inventory_charts_frame = QFrame()
        inventory_charts_layout = QHBoxLayout(inventory_charts_frame)
        
        # Inventory by category chart
        self.inventory_figure = Figure(figsize=(5, 4), dpi=100)
        self.inventory_canvas = FigureCanvas(self.inventory_figure)
        inventory_charts_layout.addWidget(self.inventory_canvas)
        
        # Inventory value chart
        self.inventory_value_figure = Figure(figsize=(5, 4), dpi=100)
        self.inventory_value_canvas = FigureCanvas(self.inventory_value_figure)
        inventory_charts_layout.addWidget(self.inventory_value_canvas)
        
        inventory_layout.addWidget(inventory_charts_frame)
        
        # Low stock table
        low_stock_group = QGroupBox("Low Stock Products")
        low_stock_layout = QVBoxLayout(low_stock_group)
        
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels(["Product", "Category", "Store Qty", "Warehouse Qty", "Min Level"])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.low_stock_table.setAlternatingRowColors(True)
        self.low_stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        low_stock_layout.addWidget(self.low_stock_table)
        inventory_layout.addWidget(low_stock_group)
        
        # Add all tabs
        self.tabs.addTab(sales_tab, "Sales Analysis")
        self.tabs.addTab(product_tab, "Product Analysis")
        self.tabs.addTab(profit_tab, "Profit Analysis")
        self.tabs.addTab(inventory_tab, "Inventory Analysis")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content_area)
        
        # Load initial data
        self.date_range_changed(2)  # Default to Last 30 Days
    
    def create_metric_widget(self, parent_layout, title, value, id_name, color):
        metric_widget = QFrame()
        metric_widget.setObjectName(id_name)
        metric_widget.setStyleSheet(f"""
            QFrame #{id_name} {{
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid {color};
            }}
        """)
        metric_layout = QVBoxLayout(metric_widget)
        metric_layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        value_label = QLabel(value)
        value_label.setObjectName(f"{id_name}_value")
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        
        metric_layout.addWidget(title_label)
        metric_layout.addWidget(value_label)
        
        parent_layout.addWidget(metric_widget)
    
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
        # Get date range
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Get period type
        period_index = self.period_combo.currentIndex()
        period_type = 'day' if period_index == 0 else 'week' if period_index == 1 else 'month'
        
        # Update all charts and tables based on the current tab
        current_tab = self.tabs.currentIndex()
        
        # Always update sales metrics as they're used in multiple tabs
        self.update_sales_metrics(start_date, end_date)
        
        if current_tab == 0:  # Sales Analysis
            self.update_sales_trend_chart(period_type, start_date, end_date)
            self.update_payment_method_chart(start_date, end_date)
            self.update_sales_by_category_chart(start_date, end_date)
        elif current_tab == 1:  # Product Analysis
            self.update_product_performance_chart(start_date, end_date)
            self.update_top_products_table(start_date, end_date)
            self.update_non_selling_table()
        elif current_tab == 2:  # Profit Analysis
            self.update_profit_metrics(start_date, end_date)
            self.update_profit_chart(start_date, end_date)
            self.update_expense_chart(start_date, end_date)
            self.update_expenses_table(start_date, end_date)
        elif current_tab == 3:  # Inventory Analysis
            self.update_inventory_metrics()
            self.update_inventory_chart()
            self.update_inventory_value_chart()
            self.update_low_stock_table()
    
    def update_sales_metrics(self, start_date, end_date):
        # Get profit analysis data which includes sales metrics
        profit_data = self.main_window.db_manager.get_profit_analysis(start_date, end_date)
        
        # Update sales metrics
        self.findChild(QLabel, "total_sales_value").setText(f"₹{profit_data['total_revenue'] or 0:.2f}")
        
        if profit_data['num_sales'] and profit_data['num_sales'] > 0:
            avg_sale = (profit_data['total_revenue'] or 0) / profit_data['num_sales']
            self.findChild(QLabel, "avg_sale_value").setText(f"₹{avg_sale:.2f}")
        else:
            self.findChild(QLabel, "avg_sale_value").setText("₹0.00")
        
        self.findChild(QLabel, "num_sales_value").setText(str(profit_data['num_sales'] or 0))
        self.findChild(QLabel, "items_sold_value").setText(str(profit_data['num_items_sold'] or 0))
    
    def update_profit_metrics(self, start_date, end_date):
        # Get profit analysis data
        profit_data = self.main_window.db_manager.get_profit_analysis(start_date, end_date)
        
        # Update profit metrics
        self.findChild(QLabel, "gross_profit_value").setText(f"₹{profit_data['gross_profit'] or 0:.2f}")
        self.findChild(QLabel, "net_profit_value").setText(f"₹{profit_data['net_profit'] or 0:.2f}")
        self.findChild(QLabel, "gross_margin_value").setText(f"{profit_data['gross_margin'] or 0:.1f}%")
        self.findChild(QLabel, "net_margin_value").setText(f"{profit_data['net_margin'] or 0:.1f}%")
    
    def update_inventory_metrics(self):
        # Get all products
        products = self.main_window.db_manager.get_all_products()
        
        # Calculate metrics
        total_products = len(products)
        store_items = sum(product['store_quantity'] for product in products)
        warehouse_items = sum(product['warehouse_quantity'] for product in products)
        low_stock_items = sum(1 for product in products if product['store_quantity'] < product['min_stock_level'])
        
        # Update inventory metrics
        self.findChild(QLabel, "total_products_value").setText(str(total_products))
        self.findChild(QLabel, "store_items_value").setText(str(store_items))
        self.findChild(QLabel, "warehouse_items_value").setText(str(warehouse_items))
        self.findChild(QLabel, "low_stock_value").setText(str(low_stock_items))
    
    def update_sales_trend_chart(self, period_type, start_date, end_date):
        # Get sales data by period
        sales_data = self.main_window.db_manager.get_sales_by_period(period_type, start_date, end_date)
        
        # Clear the figure
        self.sales_figure.clear()
        
        # Create subplot
        ax = self.sales_figure.add_subplot(111)
        
        if not sales_data:
            ax.text(0.5, 0.5, "No sales data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        else:
            # Extract dates and sales amounts
            periods = [data['period'] for data in sales_data]
            amounts = [data['final_sales'] for data in sales_data]
            num_sales = [data['num_sales'] for data in sales_data]
            
            # Create x positions
            x = np.arange(len(periods))
            
            # Plot the data
            ax.bar(x, amounts, color='#3498db', alpha=0.7, label='Sales Amount')
            
            # Create second y-axis for number of sales
            ax2 = ax.twinx()
            ax2.plot(x, num_sales, 'o-', color='#e74c3c', linewidth=2, label='Number of Sales')
            
            # Set labels and title
            period_label = 'Day' if period_type == 'day' else 'Week' if period_type == 'week' else 'Month'
            ax.set_title(f'Sales Trend by {period_label}')
            ax.set_xlabel(period_label)
            ax.set_ylabel('Amount (₹)')
            ax2.set_ylabel('Number of Sales')
            
            # Set x-axis ticks
            if len(periods) > 10:
                step = len(periods) // 10
                # Set ticks before labels
                ticks = [i for i in range(0, len(periods), step)]
                ax.set_xticks(ticks)
                ax.set_xticklabels([periods[i] for i in ticks], rotation=45)
            else:
                ax.set_xticks(range(len(periods)))
                ax.set_xticklabels(periods, rotation=45)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add legend
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Add total sales text
            total_sales = sum(amounts)
            total_transactions = sum(num_sales)
            ax.text(0.02, 0.95, f"Total: ₹{total_sales:.2f}", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))
            ax.text(0.02, 0.88, f"Transactions: {total_transactions}", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))
        
        self.sales_figure.tight_layout()
        self.sales_canvas.draw()
    
    def update_payment_method_chart(self, start_date, end_date):
        # Get payment method data from database
        payment_data = self.main_window.db_manager.get_sales_by_payment_method(start_date, end_date)
        
        # Clear the figure
        self.payment_figure.clear()
        
        # Create subplot
        ax = self.payment_figure.add_subplot(111)
        
        if not payment_data:
            ax.text(0.5, 0.5, "No sales data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        else:
            # Extract data for plotting
            methods = list(payment_data.keys())
            values = [data['percentage'] for data in payment_data.values()]
            
            # Define colors based on number of payment methods
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#34495e', '#1abc9c']
            colors = colors[:len(methods)]  # Limit colors to number of methods
            
            # Plot the data
            wedges, texts, autotexts = ax.pie(values, labels=methods, autopct='%1.1f%%', 
                                             startangle=90, colors=colors)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            ax.set_title('Sales by Payment Method')
            
            # Make text more readable
            for text in texts + autotexts:
                text.set_fontsize(9)
            
            # Add total sales amount
            total_amount = sum(data['total_amount'] for data in payment_data.values())
            ax.text(0.5, -0.1, f"Total Sales: ₹{total_amount:.2f}", 
                   horizontalalignment='center', transform=ax.transAxes, fontsize=10)
        
        self.payment_figure.tight_layout()
        self.payment_canvas.draw()
    
    def update_sales_by_category_chart(self, start_date, end_date):
        # Get sales by category data from database
        category_data = self.main_window.db_manager.get_sales_by_category(start_date, end_date)
        
        # Clear the figure
        self.category_figure.clear()
        
        # Create subplot
        ax = self.category_figure.add_subplot(111)
        
        if not category_data:
            ax.text(0.5, 0.5, "No sales data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        else:
            # Extract data for plotting
            categories = list(category_data.keys())
            
            # Calculate total revenue for percentage calculation
            total_revenue = sum(data['revenue'] for data in category_data.values())
            
            # Calculate percentages
            values = []
            for category in categories:
                if total_revenue > 0:
                    percentage = (category_data[category]['revenue'] / total_revenue) * 100
                else:
                    percentage = 0
                values.append(percentage)
            
            # Define colors based on number of categories
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#34495e', '#1abc9c']
            colors = colors[:len(categories)]  # Limit colors to number of categories
            
            # Plot the data
            ax.bar(categories, values, color=colors)
            ax.set_title('Sales by Category (%)')
            ax.set_ylabel('Percentage of Sales')
            ax.set_ylim(0, max(values) * 1.2 if values else 100)  # Set y-limit with some padding
            
            # Set ticks and rotate x-axis labels
            ax.set_xticks(range(len(categories)))  # Set the tick positions
        ax.set_xticklabels(categories, rotation=45, ha='right')  # Set the tick labels
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        self.category_figure.tight_layout()
        self.category_canvas.draw()
    
    def update_product_performance_chart(self, start_date, end_date):
        # Get top selling products
        top_products = self.main_window.db_manager.get_top_selling_products(start_date, end_date, 10)
        
        # Clear the figure
        self.product_figure.clear()
        
        # Create subplot
        ax = self.product_figure.add_subplot(111)
        
        if not top_products:
            ax.text(0.5, 0.5, "No product data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        else:
            # Extract product names and quantities
            names = [product['name'] if len(product['name']) <= 15 else product['name'][:12] + '...' 
                    for product in top_products]
            quantities = [product['total_quantity'] for product in top_products]
            revenues = [product['total_revenue'] for product in top_products]
            
            # Create x positions
            x = np.arange(len(names))
            width = 0.35
            
            # Plot the data
            ax.bar(x - width/2, quantities, width, label='Quantity', color='#3498db')
            ax2 = ax.twinx()
            ax2.bar(x + width/2, revenues, width, label='Revenue', color='#e74c3c')
            
            ax.set_title('Top Selling Products')
            ax.set_xticks(x)
            # Set ticks and rotate x-axis labels
            ax.set_xticklabels(names, rotation=45, ha='right')  # Set the tick labels
            ax.set_ylabel('Quantity Sold')
            ax2.set_ylabel('Revenue (₹)')
            
            # Add legend
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        self.product_figure.tight_layout()
        self.product_canvas.draw()
    
    def update_top_products_table(self, start_date, end_date):
        # Get top selling products
        top_products = self.main_window.db_manager.get_top_selling_products(start_date, end_date, 10)
        
        # Clear existing data
        self.top_products_table.setRowCount(0)
        
        if not top_products:
            return
        
        # Calculate total revenue for percentage
        total_revenue = sum(product['total_revenue'] for product in top_products)
        
        # Populate table
        for row, product in enumerate(top_products):
            self.top_products_table.insertRow(row)
            
            # Product Name
            self.top_products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            
            # Category
            self.top_products_table.setItem(row, 1, QTableWidgetItem(product['category'] or 'N/A'))
            
            # Quantity
            self.top_products_table.setItem(row, 2, QTableWidgetItem(str(product['total_quantity'])))
            
            # Revenue
            revenue_item = QTableWidgetItem(f"₹{product['total_revenue']:.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top_products_table.setItem(row, 3, revenue_item)
            
            # Percentage of Sales
            if total_revenue > 0:
                percentage = (product['total_revenue'] / total_revenue) * 100
                percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
            else:
                percentage_item = QTableWidgetItem("0.0%")
            percentage_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top_products_table.setItem(row, 4, percentage_item)
    
    def update_non_selling_table(self):
        # Get non-selling products
        non_selling_products = self.main_window.db_manager.get_non_selling_products(30, 10)
        
        # Clear existing data
        self.non_selling_table.setRowCount(0)
        
        # Populate table
        for row, product in enumerate(non_selling_products):
            self.non_selling_table.insertRow(row)
            
            # Product Name
            self.non_selling_table.setItem(row, 0, QTableWidgetItem(product['name']))
            
            # Category
            self.non_selling_table.setItem(row, 1, QTableWidgetItem(product['category'] or 'N/A'))
            
            # Store Quantity
            self.non_selling_table.setItem(row, 2, QTableWidgetItem(str(product['store_quantity'])))
            
            # Last Updated
            updated_at = datetime.datetime.strptime(product['updated_at'], '%Y-%m-%d %H:%M:%S')
            days_ago = (datetime.datetime.now() - updated_at).days
            updated_item = QTableWidgetItem(f"{updated_at.strftime('%Y-%m-%d')} ({days_ago} days ago)")
            self.non_selling_table.setItem(row, 3, updated_item)
    
    def update_profit_chart(self, start_date, end_date):
        # Get profit analysis data
        profit_data = self.main_window.db_manager.get_profit_analysis(start_date, end_date)
        
        # Clear the figure
        self.profit_figure.clear()
        
        # Create subplot
        ax = self.profit_figure.add_subplot(111)
        
        if not profit_data or profit_data['total_revenue'] == 0:
            ax.text(0.5, 0.5, "No profit data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
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
            colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6']
            
            # Plot the data
            bars = ax.bar(labels, values, color=colors)
            ax.set_title('Profit Analysis')
            ax.set_ylabel('Amount (₹)')
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'₹{height:.2f}', ha='center', va='bottom', rotation=45, fontsize=8)
            
            # Add margins and profit percentage
            ax.text(0.02, 0.95, f"Gross Margin: {profit_data['gross_margin']:.1f}%", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))
            ax.text(0.02, 0.88, f"Net Margin: {profit_data['net_margin']:.1f}%", transform=ax.transAxes,
                   fontsize=10, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))
        
        self.profit_figure.tight_layout()
        self.profit_canvas.draw()
    
    def update_expense_chart(self, start_date, end_date):
        # Get expenses by category data from database
        expense_data = self.main_window.db_manager.get_expenses_by_category(start_date, end_date)
        
        # Clear the figure
        self.expense_figure.clear()
        
        # Create subplot
        ax = self.expense_figure.add_subplot(111)
        
        if not expense_data:
            ax.text(0.5, 0.5, "No expense data for selected period", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        else:
            # Extract data for plotting
            categories = list(expense_data.keys())
            values = [data['percentage'] for data in expense_data.values()]
            
            # Define colors based on number of categories
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#34495e', '#1abc9c']
            colors = colors[:len(categories)]  # Limit colors to number of categories
            
            # Plot the data
            wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%', 
                                             startangle=90, colors=colors)
        
        # Always set the title
        ax.set_title('Expenses by Category')
        
        if expense_data:
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Make text more readable
            for text in texts + autotexts:
                text.set_fontsize(9)
                
            # Add total expenses amount
            total_amount = sum(data['total_amount'] for data in expense_data.values())
            ax.text(0.5, -0.1, f"Total Expenses: ₹{total_amount:.2f}", 
                   horizontalalignment='center', transform=ax.transAxes, fontsize=10)
        
        self.expense_figure.tight_layout()
        self.expense_canvas.draw()
    
    def update_expenses_table(self, start_date, end_date):
        # Get expenses
        expenses = self.main_window.db_manager.get_expenses(start_date, end_date)
        
        # Clear existing data
        self.expenses_table.setRowCount(0)
        
        # Populate table
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
            self.expenses_table.setItem(row, 4, QTableWidgetItem(expense['created_by'] or 'N/A'))
    
    def update_inventory_chart(self):
        # Get all products
        products = self.main_window.db_manager.get_all_products()
        
        # Clear the figure
        self.inventory_figure.clear()
        
        # Create subplot
        ax = self.inventory_figure.add_subplot(111)
        
        if not products:
            ax.text(0.5, 0.5, "No inventory data available", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        else:
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
            
            # Create x positions
            x = np.arange(len(cat_names))
            width = 0.35
            
            # Plot the data
            ax.bar(x - width/2, store_quantities, width, label='Store', color='#3498db')
            ax.bar(x + width/2, warehouse_quantities, width, label='Warehouse', color='#2ecc71')
            
            ax.set_title('Inventory by Category')
            ax.set_xticks(x)
            # Set ticks and rotate x-axis labels
            ax.set_xticklabels(cat_names, rotation=45, ha='right')  # Set the tick labels
            ax.set_ylabel('Quantity')
            
            # Add legend
            ax.legend()
        
        self.inventory_figure.tight_layout()
        self.inventory_canvas.draw()
    
    def update_inventory_value_chart(self):
        # Get inventory value by category data from database
        inventory_data = self.main_window.db_manager.get_inventory_value_by_category()
        
        # Clear the figure
        self.inventory_value_figure.clear()
        
        # Create subplot
        ax = self.inventory_value_figure.add_subplot(111)
        
        if not inventory_data:
            ax.text(0.5, 0.5, "No inventory data available", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        else:
            # Extract data for plotting
            categories = list(inventory_data.keys())
            values = [data['total_value'] for data in inventory_data.values()]
            total_value = sum(values)
            
            # Define colors based on number of categories
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#34495e', '#1abc9c']
            colors = colors[:len(categories)]  # Limit colors to number of categories
            
            # Plot the data
            wedges, texts, autotexts = ax.pie(values, labels=categories, 
                                             autopct=lambda p: f'₹{p * total_value / 100:.0f}', 
                                             startangle=90, colors=colors)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            ax.set_title('Inventory Value by Category')
            
            # Make text more readable
            for text in texts + autotexts:
                text.set_fontsize(9)
                
            # Add total inventory value
            ax.text(0.5, -0.1, f"Total Inventory Value: ₹{total_value:.2f}", 
                   horizontalalignment='center', transform=ax.transAxes, fontsize=10)
        
        self.inventory_value_figure.tight_layout()
        self.inventory_value_canvas.draw()
    
    def update_low_stock_table(self):
        # Get low stock products
        low_stock_products = self.main_window.db_manager.get_low_stock_products()
        
        # Clear existing data
        self.low_stock_table.setRowCount(0)
        
        # Populate table
        for row, product in enumerate(low_stock_products):
            self.low_stock_table.insertRow(row)
            
            # Product Name
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(product['name']))
            
            # Category
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(product['category'] or 'N/A'))
            
            # Store Quantity
            store_qty_item = QTableWidgetItem(str(product['store_quantity']))
            if product['store_quantity'] < product['min_stock_level']:
                store_qty_item.setForeground(QColor('#e74c3c'))  # Red for low stock
            self.low_stock_table.setItem(row, 2, store_qty_item)
            
            # Warehouse Quantity
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(str(product['warehouse_quantity'])))
            
            # Min Stock Level
            self.low_stock_table.setItem(row, 4, QTableWidgetItem(str(product['min_stock_level'])))
    
    def export_data(self):
        # Get current tab
        current_tab = self.tabs.currentIndex()
        tab_name = self.tabs.tabText(current_tab)
        
        # Get date range for filename
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Create filename
        filename = f"{tab_name.replace(' ', '_')}_{start_date}_to_{end_date}.csv"
        
        # Get file save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", filename, "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Export data based on current tab
            if current_tab == 0:  # Sales Analysis
                self.export_sales_data(file_path, start_date, end_date)
            elif current_tab == 1:  # Product Analysis
                self.export_product_data(file_path, start_date, end_date)
            elif current_tab == 2:  # Profit Analysis
                self.export_profit_data(file_path, start_date, end_date)
            elif current_tab == 3:  # Inventory Analysis
                self.export_inventory_data(file_path)
            
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export data: {str(e)}")
    
    def export_sales_data(self, file_path, start_date, end_date):
        # Get period type
        period_index = self.period_combo.currentIndex()
        period_type = 'day' if period_index == 0 else 'week' if period_index == 1 else 'month'
        
        # Get sales data
        sales_data = self.main_window.db_manager.get_sales_by_period(period_type, start_date, end_date)
        
        # Convert to DataFrame
        df = pd.DataFrame(sales_data)
        
        # Save to CSV
        df.to_csv(file_path, index=False)
    
    def export_product_data(self, file_path, start_date, end_date):
        # Get top selling products
        top_products = self.main_window.db_manager.get_top_selling_products(start_date, end_date, 50)
        
        # Convert to DataFrame
        df = pd.DataFrame(top_products)
        
        # Save to CSV
        df.to_csv(file_path, index=False)
    
    def export_profit_data(self, file_path, start_date, end_date):
        # Get profit analysis data
        profit_data = self.main_window.db_manager.get_profit_analysis(start_date, end_date)
        
        # Convert to DataFrame (need to reshape the data)
        data = {
            'Metric': ['Total Revenue', 'Total Cost', 'Total Expenses', 'Gross Profit', 'Net Profit',
                      'Gross Margin (%)', 'Net Margin (%)', 'Number of Sales', 'Number of Items Sold'],
            'Value': [
                profit_data['total_revenue'] or 0,
                profit_data['total_cost'] or 0,
                profit_data['total_expenses'] or 0,
                profit_data['gross_profit'] or 0,
                profit_data['net_profit'] or 0,
                profit_data['gross_margin'] or 0,
                profit_data['net_margin'] or 0,
                profit_data['num_sales'] or 0,
                profit_data['num_items_sold'] or 0
            ]
        }
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(file_path, index=False)
    
    def export_inventory_data(self, file_path):
        # Get all products
        products = self.main_window.db_manager.get_all_products()
        
        # Convert to DataFrame
        df = pd.DataFrame(products)
        
        # Save to CSV
        df.to_csv(file_path, index=False)
    
    def go_back(self):
        # Check if user is admin or employee
        if hasattr(self.main_window, 'admin_dashboard'):
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()