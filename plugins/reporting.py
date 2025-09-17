from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ReportingWindow(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("Reporting")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Reporting plugin – future reports can be shown here."))

PLUGIN_NAME = "Reporting"
PLUGIN_CLASS = ReportingWindow
