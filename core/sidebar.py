from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QRect

class FloatingSidebar(QWidget):
    def __init__(self, plugins, config_manager):
        super().__init__()
        self.plugins = plugins
        self.config_manager = config_manager
        self.window_refs = []

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #f5f5f5; border: 1px solid lightgray;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(6)

        for name, cls in self.plugins.items():
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("background-color:#3498db; border:none; border-radius:6px;")
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            lbl.setStyleSheet("font-weight:bold; font-size:10pt;")
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addSpacing(4)

            btn.clicked.connect(lambda _, c=cls: self.open_window(c))

    def open_window(self, window_cls):
        window = window_cls(self.config_manager)
        window.show()
        window.activateWindow()
        self.window_refs.append(window)

    def place_on_right_center(self, app, width=80):
        screen_geometry = app.primaryScreen().geometry()
        height = self.sizeHint().height()
        x = screen_geometry.width() - width - 20
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(QRect(x, y, width, height))
