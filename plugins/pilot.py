from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QApplication
from PyQt6.QtCore import QTimer
import requests, json

class ChatBox(QDialog):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("AI Chat - Pilot")
        self.resize(500, 400)
        self.config_manager = config_manager

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
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

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

PLUGIN_NAME = "Pilot"
PLUGIN_CLASS = ChatBox
