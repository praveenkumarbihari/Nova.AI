from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class AcademyWindow(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("Academy")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Academy plugin – tutorials, courses, and guides will appear here."))

PLUGIN_NAME = "Academy"
PLUGIN_CLASS = AcademyWindow
