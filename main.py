import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from core.sidebar import FloatingSidebar
from core.plugin_loader import load_plugins
from core.config import ConfigManager

def load_material_icons():
    """Load Material Icons font from various possible locations"""
    font_paths = [
        # Common installation paths for Material Icons
        "C:/Windows/Fonts/MaterialIcons-Regular.ttf",
        os.path.expanduser("~/.fonts/MaterialIcons-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "config/MaterialIcons-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "MaterialIcons-Regular.ttf"),
        # Add more paths as needed
    ]
    
    # Also try to use the font if it's already installed in the system
    existing_fonts = QFontDatabase.families()
    if "Material Icons" in existing_fonts:
        print("Material Icons font found in system fonts")
        return True
    
    # Try to load from file paths
    for font_path in font_paths:
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                print(f"Material Icons font loaded from: {font_path}")
                return True
    
    print("Warning: Material Icons font could not be loaded. Using fallback icons.")
    return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load Material Icons font
    font_loaded = load_material_icons()
    
    config = ConfigManager()
    plugins = load_plugins()

    sidebar = FloatingSidebar(plugins, config)
    sidebar.place_on_right_center(app)
    sidebar.show()
    
    sys.exit(app.exec())