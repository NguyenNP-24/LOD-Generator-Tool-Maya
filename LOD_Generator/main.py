# Entry point for the LOD Generator tool. Called to start the tool.

import importlib
import sys
from . import ui_panel, generator

def reload_all():
    """Reload modules inside LOD_Generator."""
    modules = ["LOD_Generator.ui_panel", "LOD_Generator.generator"]
    for m in modules:
        if m in sys.modules:  
            importlib.reload(sys.modules[m])
    print("LOD_Generator modules reloaded.")

def start():
    """Run LOD Generator."""
    reload_all()
    ui_panel.create_ui()
    print("LOD Generator started successfully!")
