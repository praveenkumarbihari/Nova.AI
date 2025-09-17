# core/base_plugin.py
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """
    Base plugin class. Plugins must subclass this class.
    Each plugin should accept a ConfigManager in its constructor.
    """
    name = "Unnamed"
    icon = None  # optional path to icon

    def __init__(self, config_manager):
        self.config_manager = config_manager

    @abstractmethod
    def open(self, parent=None):
        """Open plugin UI (non-blocking)."""
        raise NotImplementedError
