from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QDialog,
    QLineEdit, QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QRect
import sys
import requests
import json
import os

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


# ---------------------- Config Manager ----------------------
class ConfigManager:
    def __init__(self):
        self.config = {"llm": "gemini", "api_key": ""}
        self.load()

    def load(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
            except Exception:
                pass

    def save(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)


# ---------------------- Chat Box ----------------------
class ChatBox(QDialog):
    instances = []

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.setWindowTitle("AI Chat - Pilot")
        self.resize(500, 400)
        self.config_manager = config_manager

        ChatBox.instances.append(self)  # Keep reference to avoid auto-close

        layout = QVBoxLayout(self)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        self.user_input = QLineEdit()
        self.user_input.returnPressed.connect(self.send_message)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.user_input)
        layout.addWidget(self.send_btn)

        self.typing_label = QLabel("")
        layout.addWidget(self.typing_label)
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.animate_typing)
        self.dot_count = 0

    def send_message(self):
        text = self.user_input.text().strip()
        if not text:
            return
        self.display_message("You", text)
        self.user_input.clear()
        self.typing_label.setText("AI is typing")
        self.dot_count = 0
        self.typing_timer.start(400)
        QApplication.processEvents()
        try:
            response = self.query_llm(text)
            self.typing_timer.stop()
            self.typing_label.setText("")
            self.display_message("AI", response)
        except Exception as e:
            self.typing_timer.stop()
            self.typing_label.setText("")
            self.display_message("System", f"Error: {e}")

    def animate_typing(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.typing_label.setText("AI is typing" + "." * self.dot_count)

    def display_message(self, sender, message):
        self.chat_area.append(f"<b>{sender}:</b> {message}")
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )

    def query_llm(self, prompt):
        cfg = self.config_manager.config
        model = cfg.get("llm", "gemini")
        api_key = cfg.get("api_key", "")
        if not api_key:
            raise ValueError("API key not configured")
        if model == "gemini":
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, headers=headers, json=data)
            if r.status_code != 200:
                raise Exception(f"API error: {r.text}")
            resp = r.json()
            try:
                return resp["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                return json.dumps(resp, indent=2)
        return "Model not implemented."


# ---------------------- Settings Window ----------------------
class SettingsWindow(QWidget):
    instances = []

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.setWindowTitle("Settings")
        self.resize(350, 180)
        self.config_manager = config_manager

        SettingsWindow.instances.append(self)  # Keep reference to avoid auto-close

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.addWidget(QLabel("Select LLM:"))
        self.llm_menu = QComboBox()
        self.llm_menu.addItems(["gemini", "chatgpt", "grok"])
        self.llm_menu.setCurrentText(config_manager.config.get("llm", "gemini"))
        layout.addWidget(self.llm_menu)

        layout.addWidget(QLabel("API Key:"))
        self.api_entry = QLineEdit()
        self.api_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_entry.setText(config_manager.config.get("api_key", ""))
        layout.addWidget(self.api_entry)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

    def save_config(self):
        self.config_manager.config["llm"] = self.llm_menu.currentText()
        self.config_manager.config["api_key"] = self.api_entry.text().strip()
        self.config_manager.save()
        QMessageBox.information(self, "Settings", "Configuration saved successfully.")
        self.close()


# ---------------------- Floating Sidebar ----------------------
class FloatingSidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("background-color: #f5f5f5; border: 1px solid lightgray;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # Define buttons: label, color, window class
        self.buttons = [
            ("Pilot", "#e74c3c", ChatBox),
            ("Tools", "#3498db", None),
            ("Setting", "#2ecc71", SettingsWindow),
            ("Reporting", "#f39c12", None),
            ("Academy", "#9b59b6", None)
        ]

        self.window_refs = []  # Keep references to prevent auto-close

        for label, color, window_cls in self.buttons:
            btn = QPushButton()
            btn.setStyleSheet(f"background-color:{color}; border:none; min-height:40px;")
            btn.setFixedSize(40, 40)
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            lbl.setStyleSheet("font-weight:bold; font-size:10pt;")
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addSpacing(5)

            if window_cls:
                btn.clicked.connect(lambda _, cls=window_cls: self.open_window(cls))

    def open_window(self, window_cls):
        window = window_cls(self.config_manager)
        window.show()  # Non-blocking
        window.activateWindow()
        self.window_refs.append(window)  # Keep reference


# ---------------------- Main ----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    sidebar = FloatingSidebar()

    screen_geometry = app.primaryScreen().geometry()
    width = 80
    height = sidebar.sizeHint().height()
    x = screen_geometry.width() - width - 20
    y = (screen_geometry.height() - height) // 2
    sidebar.setGeometry(QRect(x, y, width, height))
    sidebar.show()

    sys.exit(app.exec())
