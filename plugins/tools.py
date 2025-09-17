from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ToolsWindow(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("Tools")
        self.resize(300, 200)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("This is the Tools plugin window."))

PLUGIN_NAME = "Tools"
PLUGIN_CLASS = ToolsWindow
