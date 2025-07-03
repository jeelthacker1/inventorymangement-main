import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from pyzbar.pyzbar import decode

class QRScannerScreen(QWidget):
    # Signal to emit when a QR code is successfully scanned
    qr_scanned = pyqtSignal(str)
    
    def __init__(self, main_window, callback=None):
        super().__init__()
        self.main_window = main_window
        self.callback = callback  # Function to call when QR code is scanned
        self.camera = None
        self.timer = None
        self.available_cameras = []
        self.current_camera_index = 0
        self.last_scanned_code = None
        self.last_scan_time = 0
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
        
        title_label = QLabel("QR Code Scanner")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        top_bar_layout.addWidget(back_btn)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        
        main_layout.addWidget(top_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f5f5;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Camera selection
        camera_frame = QFrame()
        camera_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
            }
        """)
        camera_layout = QHBoxLayout(camera_frame)
        
        camera_label = QLabel("Select Camera:")
        camera_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
        self.camera_combo = QComboBox()
        self.camera_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
        """)
        self.camera_combo.currentIndexChanged.connect(self.change_camera)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.refresh_cameras)
        
        camera_layout.addWidget(camera_label)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.addWidget(refresh_btn)
        
        content_layout.addWidget(camera_frame)
        
        # Camera view
        self.camera_view = QLabel()
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setMinimumSize(640, 480)
        self.camera_view.setStyleSheet("""
            QLabel {
                background-color: black;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        content_layout.addWidget(self.camera_view)
        
        # Status and manual entry
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Ready to scan QR code...")
        self.status_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        
        status_layout.addWidget(self.status_label)
        
        content_layout.addWidget(status_frame)
        
        main_layout.addWidget(content_widget)
        
        # Initialize camera
        self.refresh_cameras()
    
    def go_back(self):
        # Stop camera before going back
        self.stop_camera()
        
        # Check if user is admin or employee
        if hasattr(self.main_window, 'admin_dashboard'):
            self.main_window.show_admin_dashboard()
        else:
            self.main_window.show_employee_dashboard()
    
    def refresh_cameras(self):
        # Stop current camera if running
        self.stop_camera()
        
        # Clear combo box
        self.camera_combo.clear()
        self.available_cameras = []
        
        # Find available cameras
        max_cameras = 5  # Check up to 5 cameras
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.available_cameras.append(i)
                self.camera_combo.addItem(f"Camera {i}")
                cap.release()
        
        if not self.available_cameras:
            self.status_label.setText("No cameras found. Please connect a camera and refresh.")
            self.status_label.setStyleSheet("font-size: 14px; color: #e74c3c;")
        else:
            # Start the first available camera
            self.current_camera_index = 0
            self.camera_combo.setCurrentIndex(0)
            self.start_camera()
    
    def change_camera(self, index):
        if index < 0 or index >= len(self.available_cameras):
            return
        
        # Stop current camera
        self.stop_camera()
        
        # Update current camera index
        self.current_camera_index = index
        
        # Start new camera
        self.start_camera()
    
    def start_camera(self):
        if not self.available_cameras:
            return
        
        # Initialize camera
        camera_index = self.available_cameras[self.current_camera_index]
        self.camera = cv2.VideoCapture(camera_index)
        
        if not self.camera.isOpened():
            self.status_label.setText(f"Failed to open camera {camera_index}. Please try another camera.")
            self.status_label.setStyleSheet("font-size: 14px; color: #e74c3c;")
            return
        
        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Start timer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms (approx. 33 fps)
        
        self.status_label.setText("Camera started. Scanning for QR codes...")
        self.status_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
    
    def stop_camera(self):
        # Stop timer
        if self.timer and self.timer.isActive():
            self.timer.stop()
        
        # Release camera
        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
    
    def update_frame(self):
        if not self.camera or not self.camera.isOpened():
            return
        
        # Read frame from camera
        ret, frame = self.camera.read()
        
        if not ret:
            self.status_label.setText("Failed to read frame from camera. Please try another camera.")
            self.status_label.setStyleSheet("font-size: 14px; color: #e74c3c;")
            self.stop_camera()
            return
        
        # Scan for QR codes
        self.scan_qr_codes(frame)
        
        # Convert frame to QImage for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale to fit the label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_img)
        self.camera_view.setPixmap(pixmap.scaled(self.camera_view.size(), Qt.KeepAspectRatio))
    
    def scan_qr_codes(self, frame):
        import time
        current_time = time.time()
        
        # Only process every 0.5 seconds to avoid multiple scans of the same code
        if current_time - self.last_scan_time < 0.5:
            return
        
        # Convert to grayscale for better QR detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Scan for QR codes
        qr_codes = decode(gray)
        
        for qr_code in qr_codes:
            # Get QR code data
            qr_data = qr_code.data.decode('utf-8')
            
            # Check if this is a new code (to avoid multiple scans of the same code)
            if qr_data != self.last_scanned_code:
                self.last_scanned_code = qr_data
                self.last_scan_time = current_time
                
                # Update status
                self.status_label.setText(f"QR Code detected: {qr_data}")
                self.status_label.setStyleSheet("font-size: 14px; color: #27ae60;")
                
                # Emit signal
                self.qr_scanned.emit(qr_data)
                
                # Call callback if provided
                if self.callback:
                    # Stop camera before calling callback
                    self.stop_camera()
                    
                    # Call callback with QR data
                    self.callback(qr_data)
                    
                    # Go back to previous screen
                    self.go_back()
                    
                    return
    
    def closeEvent(self, event):
        # Stop camera when widget is closed
        self.stop_camera()
        super().closeEvent(event)
        
    def set_callback(self, callback):
        # Set the callback function to be called when a QR code is scanned
        self.callback = callback