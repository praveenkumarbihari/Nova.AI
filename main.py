import sys
from PyQt6.QtWidgets import QApplication
from core.sidebar import FloatingSidebar
from core.plugin_loader import load_plugins
from core.config import ConfigManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    config = ConfigManager()
    plugins = load_plugins()

    sidebar = FloatingSidebar(plugins, config)
    sidebar.place_on_right_center(app)
    sidebar.show()
    sys.exit(app.exec())
