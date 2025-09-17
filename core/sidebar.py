from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QLinearGradient, QFont, QFontDatabase

class FloatingSidebar(QWidget):
    def __init__(self, plugins, config_manager):
        super().__init__()
        self.plugins = plugins
        self.config_manager = config_manager
        self.window_refs = []
        self.is_collapsed = False
        self.animation = None

        # Check if Material Icons font is available
        self.material_icons_available = "Material Icons" in QFontDatabase.families()
        
        # Set window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(12)
        
        # Add title
        title = QLabel("Nova AI")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
                padding-bottom: 5px;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        layout.addWidget(title)
        
        # Material Icons Unicode mapping
        material_icons = {
            "Pilot": "\ue8e8",        # Chat icon
            "Browser": "\ue89e",      # Public icon
            "Notes": "\ue262",        # Notes icon
            "Calculator": "\uf1ec",   # Calculate icon
            "Settings": "\ue8b8",     # Settings icon
            "Music": "\ue405",        # Music note icon
            "Files": "\ue2c7",        # Folder icon
            "Camera": "\ue3af",       # Camera icon
            "Weather": "\ue63d",      # Weather icon
            "Calendar": "\ue935",     # Calendar icon
            "Mail": "\ue158",         # Mail icon
            "Map": "\ue55f",          # Map icon
            "Photos": "\ue413",       # Photo library icon
            "Contacts": "\ue7fd",     # Contacts icon
        }
        
        # Fallback text icons if Material Icons not available
        fallback_icons = {
            "Pilot": "💬",        # Chat bubble
            "Browser": "🌐",      # Globe
            "Notes": "📝",        # Notepad
            "Calculator": "🧮",   # Calculator
            "Settings": "⚙️",     # Gear
            "Music": "🎵",        # Music note
            "Files": "📁",        # Folder
            "Camera": "📷",       # Camera
            "Weather": "☀️",      # Sun
            "Calendar": "📅",     # Calendar
            "Mail": "✉️",         # Envelope
            "Map": "🗺️",          # Map
            "Photos": "🖼️",       # Picture
            "Contacts": "👤",     # Person
        }
        
        # Add plugin buttons
        for name, cls in self.plugins.items():
            # Create button
            btn = QPushButton()
            btn.setFixedSize(50, 50)
            btn.setProperty("pluginName", name)
            
            # Set icon based on availability
            if self.material_icons_available:
                btn.setText(material_icons.get(name, "\ue88a"))  # Default: Apps icon
                icon_font = QFont("Material Icons")
                icon_font.setPointSize(24)
                btn.setFont(icon_font)
            else:
                btn.setText(fallback_icons.get(name, "📱"))  # Default: Smartphone icon
                btn.setFont(QFont("Arial", 16))
            
            # Style for all buttons
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    border: none;
                    border-radius: 25px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                    border: 2px solid white;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                    padding-top: 2px;
                    padding-left: 2px;
                }
            """)
            
            # Add label
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            lbl.setStyleSheet("""
                QLabel {
                    color: #7f8c8d;
                    font-weight: 500;
                    font-size: 9px;
                    margin-top: 2px;
                }
            """)
            
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
            
            # Connect button click
            btn.clicked.connect(lambda _, c=cls, n=name: self.open_window(c, n))
        
        # Add spacer to push content to top
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        
        # Add toggle button
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(30, 20)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                border: none;
                border-radius: 4px;
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Set initial size
        self.setFixedWidth(90)

    def paintEvent(self, event):
        """Draw rounded corners and shadow effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))
        path.addRoundedRect(rect, 15, 15)
        
        # Fill with gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(245, 245, 245))
        gradient.setColorAt(1, QColor(235, 235, 235))
        
        painter.fillPath(path, gradient)
        
        # Draw border
        painter.setPen(QColor(220, 220, 220))
        painter.drawPath(path)

    def open_window(self, window_cls, plugin_name):
        """Open a new independent window"""
        # Create the window with None as parent to make it independent
        window = window_cls(self.config_manager, None)
        
        # Store reference to prevent garbage collection
        self.window_refs.append(window)
        
        # Remove the window from our references when it's closed
        window.destroyed.connect(lambda: self.window_refs.remove(window))
        
        window.show()
        window.activateWindow()
        
        # Optional: Add a subtle animation when opening a window
        self.animate_click(plugin_name)

    def animate_click(self, plugin_name):
        """Animate button click effect"""
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.property("pluginName") == plugin_name:
                # Create animation
                animation = QPropertyAnimation(widget, b"geometry")
                animation.setDuration(150)
                animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                
                start_rect = widget.geometry()
                animation.setStartValue(start_rect)
                animation.setKeyValueAt(0.5, start_rect.adjusted(-2, -2, 2, 2))
                animation.setEndValue(start_rect)
                
                animation.start()
                break

    def toggle_sidebar(self):
        """Toggle sidebar collapse/expand"""
        self.is_collapsed = not self.is_collapsed
        
        if self.animation and self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        current_rect = self.geometry()
        if self.is_collapsed:
            self.animation.setStartValue(current_rect)
            self.animation.setEndValue(QRect(current_rect.x() + 70, current_rect.y(), 20, current_rect.height()))
            self.toggle_btn.setText("▶")
            
            # Hide all widgets except toggle button
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if widget and widget != self.toggle_btn:
                    widget.hide()
        else:
            self.animation.setStartValue(current_rect)
            self.animation.setEndValue(QRect(current_rect.x() - 70, current_rect.y(), 90, current_rect.height()))
            self.toggle_btn.setText("◀")
            
            # Show all widgets
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if widget:
                    widget.show()
        
        self.animation.start()

    def place_on_right_center(self, app, width=90):
        screen_geometry = app.primaryScreen().geometry()
        height = self.sizeHint().height()
        x = screen_geometry.width() - width - 20
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(QRect(x, y, width, height))
        
        # Set minimum height to prevent cutting off content
        self.setMinimumHeight(height)