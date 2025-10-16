import os
import shutil
import maya.cmds as cmds

def onMayaDroppedPythonFile(*args):
    """
    Maya entry point when this install script is dragged into the viewport.
    """
    try:
        install_tool()
    except Exception as e:
        cmds.warning(f"[LOD Generator Installer] Error: {e}")

def install_tool():
    """
    Main installation logic for LOD Generator.
    - Removes any old installation of LOD_Generator.
    - Copies the new files into the Maya scripts folder.
    - Adds the shelf button automatically.
    """

    # Detect Maya scripts directory
    scripts_dir = os.path.join(cmds.internalVar(userAppDir=True), "scripts")
    install_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(scripts_dir, "LOD_Generator")

    print(f"[LOD Generator Installer] Maya scripts folder: {scripts_dir}")
    print(f"[LOD Generator Installer] Install source: {install_dir}")

    # --- Remove all old LOD_Generator folders ---
    for root, dirs, _ in os.walk(scripts_dir):
        for d in dirs:
            if d == "LOD_Generator":
                old_path = os.path.join(root, d)
                try:
                    shutil.rmtree(old_path)
                    print(f"[LOD Generator Installer] Removed old folder: {old_path}")
                except Exception as e:
                    cmds.warning(f"Failed to remove {old_path}: {e}")

    # --- Copy new files ---
    try:
        shutil.copytree(install_dir, target_dir)
        print(f"[LOD Generator Installer] Installed to: {target_dir}")
    except Exception as e:
        cmds.warning(f"Failed to copy files: {e}")
        return

    # --- Add Shelf Button ---
    add_shelf_button(target_dir)

    cmds.inViewMessage(
        amg="<hl>LOD Generator installed successfully!</hl>",
        pos="midCenter",
        fade=True
    )

def add_shelf_button(tool_dir):
    """
    Adds a new shelf button for the LOD Generator tool.
    If the shelf already exists, the old button will be replaced.
    """

    shelf_name = "Custom"
    icon_path = os.path.join(tool_dir, "icon.png")

    # Try to find or create shelf tab
    if not cmds.shelfLayout(shelf_name, exists=True):
        shelf_name = cmds.shelfLayout(shelf_name, p="ShelfLayout")

    # Remove any existing button with same label
    buttons = cmds.shelfLayout(shelf_name, q=True, ca=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, q=True, label=True) == "LOD Generator":
            cmds.deleteUI(btn)

    # Create new shelf button
    cmds.shelfButton(
        parent=shelf_name,
        label="LOD Generator",
        annotation="Launch LOD Generator Tool",
        image1=icon_path if os.path.exists(icon_path) else "commandButton.png",
        command='import LOD_Generator.main as main; main.start()'
    )

    print(f"[LOD Generator Installer] Shelf button added to: {shelf_name}")

# Execute immediately if run directly
if __name__ == "__main__":
    install_tool()
