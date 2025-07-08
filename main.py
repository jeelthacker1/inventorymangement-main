import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QMessageBox,
                             QWidget, QVBoxLayout, QLabel, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Import all application screens
from screens.login import LoginScreen
from screens.employee_dashboard import EmployeeDashboard
from screens.admin_dashboard import AdminDashboard
from screens.product_management import ProductManagement
from screens.sales import SalesScreen
from screens.repair import RepairScreen
from screens.analytics import AnalyticsScreen
from screens.invoice import InvoiceScreen as InvoiceGenerator
# Add this import for repair invoice functionality
from screens.repair_invoice import RepairInvoiceScreen

# Set QR scanner availability flag
QR_SCANNER_AVAILABLE = False

# Define a placeholder class for QRScannerScreen when not available
class QRScannerScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        
        message = QLabel("QR Scanner functionality is not available.")
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("font-size: 16px; color: #555;")
        
        instructions = QLabel(
            "Please install Visual C++ Redistributable Packages for Visual Studio 2013:\n"
            "1. Download from: https://aka.ms/highdpimfc2013x64enu (64-bit) or\n"
            "   https://aka.ms/highdpimfc2013x86enu (32-bit)\n"
            "2. Install the package\n"
            "3. Restart the application"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("font-size: 14px; color: #777;")
        instructions.setWordWrap(True)
        
        back_button = QPushButton("Back to Dashboard")
        back_button.setFixedWidth(200)
        back_button.clicked.connect(lambda: self.main_window.show_employee_dashboard() 
                                   if self.main_window.login_screen.current_user_role == "employee" 
                                   else self.main_window.show_admin_dashboard())
        
        layout.addStretch(1)
        layout.addWidget(message)
        layout.addSpacing(20)
        layout.addWidget(instructions)
        layout.addSpacing(30)
        layout.addWidget(back_button, 0, Qt.AlignCenter)
        layout.addStretch(1)
        
    def refresh_data(self):
        # Dummy method to match the interface of the real QRScannerScreen
        pass

# Print a message about QR scanner functionality
print("QR Scanner functionality is not available due to missing dependencies.")
print("Please install Visual C++ Redistributable Packages for Visual Studio 2013:")
print("Download from: https://aka.ms/highdpimfc2013x64enu (64-bit) or https://aka.ms/highdpimfc2013x86enu (32-bit)")
print("The application will continue without QR scanning functionality.\n")

from screens.customer import CustomerScreen

# Import database manager
from database.db_manager import DatabaseManager

class InventoryManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        self.db_manager.setup_database()
        
        # Set up the stacked widget to manage different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Track authentication state
        self.is_authenticated = False
        self.current_user_role = None
        
        # Initialize all screens
        self.init_screens()
        
        # Start with login screen
        self.show_login_screen()
        
    def init_screens(self):
        # Create all application screens
        self.login_screen = LoginScreen(self)
        self.employee_dashboard = EmployeeDashboard(self)
        self.admin_dashboard = AdminDashboard(self)
        self.product_management = ProductManagement(self)
        self.sales_screen = SalesScreen(self)
        self.repair_screen = RepairScreen(self)
        self.analytics_screen = AnalyticsScreen(self)
        self.invoice_generator = InvoiceGenerator(self)
        self.customer_screen = CustomerScreen(self)
        
        # Initialize QR scanner (will use dummy class if real one is not available)
        self.qr_scanner = QRScannerScreen(self)
        if not QR_SCANNER_AVAILABLE:
            print("QR Scanner functionality is not available due to missing dependencies.")
        
        # Add all screens to the stacked widget
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.employee_dashboard)
        self.stacked_widget.addWidget(self.admin_dashboard)
        self.stacked_widget.addWidget(self.product_management)
        self.stacked_widget.addWidget(self.sales_screen)
        self.stacked_widget.addWidget(self.repair_screen)
        self.stacked_widget.addWidget(self.analytics_screen)
        self.stacked_widget.addWidget(self.invoice_generator)
        self.stacked_widget.addWidget(self.customer_screen)
        self.stacked_widget.addWidget(self.qr_scanner)
    
    # Navigation methods
    def show_login_screen(self):
        # Reset authentication state when showing login screen
        self.is_authenticated = False
        self.current_user_role = None
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def show_employee_dashboard(self):
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.employee_dashboard)
        self.employee_dashboard.refresh_data()
    
    def show_admin_dashboard(self):
        # Check if user is authenticated as admin
        if not self.is_authenticated or self.current_user_role != 'admin':
            QMessageBox.warning(self, "Access Denied", "You must be logged in as an administrator to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.admin_dashboard)
        self.admin_dashboard.refresh_data()
    
    def show_product_management(self):
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.product_management)
        self.product_management.refresh_data()
    
    def show_sales_screen(self):
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.sales_screen)
        self.sales_screen.refresh_data()
    
    def show_repair_screen(self):
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.repair_screen)
        self.repair_screen.refresh_data()
    
    def show_analytics_screen(self):
        # Check if user is authenticated as admin
        if not self.is_authenticated or self.current_user_role != 'admin':
            QMessageBox.warning(self, "Access Denied", "You must be logged in as an administrator to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.analytics_screen)
        self.analytics_screen.refresh_data()
    
    def show_invoice_generator(self, sale_id=None):
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.invoice_generator)
        if sale_id:
            self.invoice_generator.sale_id = sale_id
            self.invoice_generator.load_sale_data()
    
    def show_repair_invoice(self, repair_id):
        # Clear current central widget if exists
        if hasattr(self, 'current_screen'):
            self.current_screen.deleteLater()
        
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        # Add debugging logs
        print(f"Showing repair invoice for repair_id: {repair_id}")
        
        # Check if repair exists
        repair_data = self.db_manager.get_repair(repair_id)
        if not repair_data:
            print(f"Error: Repair data not found for repair_id: {repair_id}")
            QMessageBox.critical(self, "Error", "Repair data not found. Cannot generate invoice.")
            return
        
        print(f"Repair data found: {repair_data}")
        
        # Check if repair has parts
        repair_parts = self.db_manager.get_repair_parts(repair_id)
        print(f"Repair parts found: {len(repair_parts)} parts")
        
        # Create and show repair invoice screen
        self.current_screen = RepairInvoiceScreen(self, repair_id)
        self.setCentralWidget(self.current_screen)
        self.current_screen.show()
        print(f"RepairInvoiceScreen created and shown for repair_id: {repair_id}")
    
    def show_qr_scanner(self, callback=None):
        if QR_SCANNER_AVAILABLE:
            # If a callback is provided, set it in the QR scanner
            if callback:
                self.qr_scanner.set_callback(callback)
            self.stacked_widget.setCurrentWidget(self.qr_scanner)
        else:
            QMessageBox.warning(self, "Feature Unavailable", 
                "QR Scanner functionality is not available due to missing dependencies.\n\n"
                "Please install Visual C++ Redistributable Packages for Visual Studio 2013:\n"
                "1. Download from: https://aka.ms/highdpimfc2013x64enu (64-bit) or\n"
                "   https://aka.ms/highdpimfc2013x86enu (32-bit)\n"
                "2. Install the package\n"
                "3. Restart the application")
    
    def show_expense_screen(self):
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        # Import ExpenseScreen if not already imported
        from screens.expense import ExpenseScreen
        
        # Create and add the expense screen to the stacked widget if it doesn't exist
        if not hasattr(self, 'expense_screen'):
            self.expense_screen = ExpenseScreen(self)
            self.stacked_widget.addWidget(self.expense_screen)
        
        # Show the expense screen
        self.stacked_widget.setCurrentWidget(self.expense_screen)
        self.expense_screen.load_expenses()
    
    def show_customer_screen(self):
        # Check if user is authenticated
        if not self.is_authenticated:
            QMessageBox.warning(self, "Access Denied", "You must be logged in to access this page.")
            self.show_login_screen()
            return
            
        self.stacked_widget.setCurrentWidget(self.customer_screen)
        self.customer_screen.load_customers()
    
    def logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Reset authentication state
            self.is_authenticated = False
            self.current_user_role = None
            self.show_login_screen()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look
    
    # Set application icon
    # app.setWindowIcon(QIcon('assets/icon.png'))
    
    # Apply stylesheet for custom styling if it exists
    try:
        with open('assets/style.qss', 'r') as f:
            style = f.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print("Warning: Could not find stylesheet file 'assets/style.qss'. Using default styling.")
        # Apply some basic styling
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QLabel {
                color: #333;
            }
        """)
    
    window = InventoryManagementSystem()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()