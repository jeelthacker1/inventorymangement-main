import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QStackedWidget, QCheckBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont

class LoginScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # Left side - Logo and welcome message
        left_panel = QFrame()
        left_panel.setObjectName("login-left-panel")
        left_panel.setStyleSheet("#login-left-panel { background-color: #2c3e50; }")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Logo placeholder
        logo_label = QLabel()
        # If you have a logo file, uncomment the following line
        # logo_label.setPixmap(QPixmap("assets/logo.png").scaled(200, 200, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        left_layout.addWidget(logo_label)
        
        # Welcome text
        welcome_label = QLabel("Inventory Management System")
        welcome_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        welcome_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(welcome_label)
        
        description_label = QLabel("Manage your inventory, sales, and repairs efficiently")
        description_label.setStyleSheet("color: #ecf0f1; font-size: 16px;")
        description_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(description_label)
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Right side - Login form
        right_panel = QFrame()
        right_panel.setObjectName("login-right-panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(50, 50, 50, 50)
        
        # Stacked widget for employee and admin login forms
        self.login_stack = QStackedWidget()
        right_layout.addWidget(self.login_stack)
        
        # Employee login form
        employee_widget = QWidget()
        employee_layout = QVBoxLayout(employee_widget)
        employee_layout.setAlignment(Qt.AlignCenter)
        employee_layout.setSpacing(20)
        
        employee_title = QLabel("Employee Login")
        employee_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        employee_title.setAlignment(Qt.AlignCenter)
        employee_layout.addWidget(employee_title)
        
        employee_subtitle = QLabel("Quick access for employees")
        employee_subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        employee_subtitle.setAlignment(Qt.AlignCenter)
        employee_layout.addWidget(employee_subtitle)
        
        employee_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Employee login button
        employee_login_btn = QPushButton("Login as Employee")
        employee_login_btn.setMinimumHeight(50)
        employee_login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        employee_login_btn.clicked.connect(self.employee_login)
        employee_layout.addWidget(employee_login_btn)
        
        employee_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Switch to admin login
        switch_to_admin_btn = QPushButton("Admin Login")
        switch_to_admin_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                font-size: 14px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        switch_to_admin_btn.clicked.connect(lambda: self.login_stack.setCurrentIndex(1))
        employee_layout.addWidget(switch_to_admin_btn)
        
        # Admin login form
        admin_widget = QWidget()
        admin_layout = QVBoxLayout(admin_widget)
        admin_layout.setAlignment(Qt.AlignCenter)
        admin_layout.setSpacing(20)
        
        admin_title = QLabel("Admin Login")
        admin_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        admin_title.setAlignment(Qt.AlignCenter)
        admin_layout.addWidget(admin_title)
        
        admin_subtitle = QLabel("Access admin features with your credentials")
        admin_subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        admin_subtitle.setAlignment(Qt.AlignCenter)
        admin_layout.addWidget(admin_subtitle)
        
        admin_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Username field
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        admin_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        admin_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        admin_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        admin_layout.addWidget(self.password_input)
        
        # Show password checkbox
        show_password_cb = QCheckBox("Show password")
        show_password_cb.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        show_password_cb.toggled.connect(self.toggle_password_visibility)
        admin_layout.addWidget(show_password_cb)
        
        admin_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Admin login button
        admin_login_btn = QPushButton("Login")
        admin_login_btn.setMinimumHeight(50)
        admin_login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        admin_login_btn.clicked.connect(self.admin_login)
        admin_layout.addWidget(admin_login_btn)
        
        # Switch to employee login
        switch_to_employee_btn = QPushButton("Employee Login")
        switch_to_employee_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                font-size: 14px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        switch_to_employee_btn.clicked.connect(lambda: self.login_stack.setCurrentIndex(0))
        admin_layout.addWidget(switch_to_employee_btn)
        
        # Add both forms to the stacked widget
        self.login_stack.addWidget(employee_widget)
        self.login_stack.addWidget(admin_widget)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)  # 1 part for left panel
        main_layout.addWidget(right_panel, 1)  # 1 part for right panel
        
        # Set default to employee login
        self.login_stack.setCurrentIndex(0)
    
    def toggle_password_visibility(self, show):
        if show:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def employee_login(self):
        # Employee login doesn't require password
        user = self.main_window.db_manager.authenticate_user('employee')
        if user:
            # Set authentication state
            self.main_window.is_authenticated = True
            self.main_window.current_user_role = 'employee'
            self.main_window.show_employee_dashboard()
        else:
            QMessageBox.warning(self, "Login Failed", "Employee login is not available. Please contact administrator.")
    
    def admin_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
        
        user = self.main_window.db_manager.authenticate_user(username, password)
        if user and user['role'] == 'admin':
            # Set authentication state
            self.main_window.is_authenticated = True
            self.main_window.current_user_role = 'admin'
            self.main_window.show_admin_dashboard()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.password_input.clear()