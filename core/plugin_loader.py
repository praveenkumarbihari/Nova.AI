import os, importlib

def load_plugins():
    plugins = {}
    plugin_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")
    plugin_dir = os.path.abspath(plugin_dir)

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            module_path = f"plugins.{module_name}"
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "PLUGIN_NAME") and hasattr(module, "PLUGIN_CLASS"):
                    plugins[module.PLUGIN_NAME] = module.PLUGIN_CLASS
            except Exception as e:
                print(f"⚠️ Failed to load {module_name}: {e}")

    # ✅ enforce fixed order
    desired_order = ["Pilot", "Tools", "Settings", "Reporting", "Academy"]
    ordered_plugins = {name: plugins[name] for name in desired_order if name in plugins}

    return ordered_plugins
