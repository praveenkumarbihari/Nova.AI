from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox

class SettingsWindow(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("Settings")
        self.resize(350, 180)
        self.config_manager = config_manager

        layout = QVBoxLayout(self)
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

PLUGIN_NAME = "Settings"
PLUGIN_CLASS = SettingsWindow
