# Developer reload script — only for development use, not for production.
# This script reloads the LOD_Generator modules and restarts the tool.
# Paste to Maya script editor and run to reload the tool.

import sys 
import importlib 

# Adjust the path to your LOD_Generator folder
tool_path = r"C:\Users\Hi\Desktop\Ubisoft-Test"
if tool_path not in sys.path:
    sys.path.append(tool_path)

# Reload modules
import LOD_Generator.main # type: ignore
importlib.reload(LOD_Generator.main)
LOD_Generator.main.start()
