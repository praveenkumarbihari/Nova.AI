from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLineEdit, 
                             QPushButton, QLabel, QApplication, QHBoxLayout,
                             QSizePolicy)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
import requests, json

class ChatBox(QWidget):
    # Signal to notify when window state changes
    windowStateChanged = pyqtSignal(bool)
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent, Qt.WindowType.Window)  # Critical fix: Set window flag here
        self.config_manager = config_manager
        self.is_maximized = False
        self.normal_geometry = None
        
        # Set window properties
        self.setWindowTitle("Nova Chat - Pilot")
        # Remove window flags from here - they cause issues
        self.resize(500, 400)
        
        # Set application style
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f7;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0062a3;
            }
            QPushButton:pressed {
                background-color: #004d80;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #666666;
            }
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Create chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.chat_area)
        
        # Create input area with horizontal layout
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Create typing indicator
        self.typing_label = QLabel("")
        self.typing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.typing_label.setVisible(False)
        layout.addWidget(self.typing_label)
        
        # Initialize typing timer
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.animate_typing)
        self.dot_count = 0
        
        # Add welcome message
        QTimer.singleShot(100, self.show_welcome_message)
        
    def show_welcome_message(self):
        """Display a welcome message when the chat opens"""
        self.display_message("AI", "Hey Praveen! How's it going?", is_welcome=True)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double click on title bar to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 40:
            self.toggle_maximize()
        super().mouseDoubleClickEvent(event)
            
    def toggle_maximize(self):
        """Toggle between maximized and normal state"""
        if self.is_maximized:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
        else:
            self.normal_geometry = self.geometry()
            self.showMaximized()
            
        self.is_maximized = not self.is_maximized
        self.windowStateChanged.emit(self.is_maximized)
        
    def send_message(self):
        """Send user message and get AI response"""
        text = self.user_input.text().strip()
        if not text:
            return
            
        # Disable input while processing
        self.user_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        
        # Display user message
        self.display_message("You", text)
        self.user_input.clear()
        
        # Show typing indicator
        self.typing_label.setVisible(True)
        self.dot_count = 0
        self.typing_timer.start(400)
        
        # Process the message (using a timer to simulate async processing)
        QTimer.singleShot(100, lambda: self.process_ai_response(text))
        
    def process_ai_response(self, user_message):
        """Process the user message and get AI response"""
        try:
            response = self.query_llm(user_message)
            self.typing_timer.stop()
            self.typing_label.setVisible(False)
            self.display_message("AI", response)
        except Exception as e:
            self.typing_timer.stop()
            self.typing_label.setVisible(False)
            self.display_message("System", f"Error: {str(e)}")
        finally:
            # Re-enable input
            self.user_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.user_input.setFocus()
        
    def animate_typing(self):
        """Animate the typing indicator"""
        self.dot_count = (self.dot_count + 1) % 4
        self.typing_label.setText("AI is typing" + "." * self.dot_count)
        
    def display_message(self, sender, message, is_welcome=False):
        """Display a message in the chat area with appropriate styling"""
        # Different colors for different senders
        colors = {
            "You": "#007acc",
            "AI": "#4caf50", 
            "System": "#ff5722"
        }
        
        color = colors.get(sender, "#000000")
        
        # Format the message with HTML
        formatted_message = f"""
        <div style="margin-bottom: 12px;">
            <span style="font-weight: 600; color: {color};">{sender}:</span>
            <span style="color: #333333;">{message}</span>
        </div>
        """
        
        # Insert the message
        self.chat_area.append(formatted_message)
        
        # Scroll to bottom
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def query_llm(self, prompt):
        """Query the LLM API"""
        cfg = self.config_manager.config
        model = cfg.get("llm", "gemini")
        api_key = cfg.get("api_key", "")
        
        if not api_key:
            raise ValueError("API key not configured. Please set it in the settings.")
            
        if model == "gemini":
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                error_msg = response.json().get('error', {}).get('message', 'Unknown API error')
                raise Exception(f"API error: {error_msg}")
                
            resp = response.json()
            
            try:
                return resp["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                # If the response format is unexpected, return the raw JSON for debugging
                return json.dumps(resp, indent=2)
                
        return "Selected model is not implemented yet."


PLUGIN_NAME = "Pilot"
PLUGIN_CLASS = ChatBox