import os
import shutil
import maya.cmds as cmds # type: ignore

def install_tool():
    """
    Automatic installation for LOD_Generator:
    - Copy the LOD_Generator folder into Maya's scripts folder
    - Create a Shelf button if desired
    """
    # Directory containing this install file
    src = os.path.dirname(__file__)

    # Maya scripts directory
    dst = os.path.join(cmds.internalVar(userScriptDir=True), "LOD_Generator")

    # If it already exists, remove it first
    if os.path.exists(dst):
        shutil.rmtree(dst)

    # Copy the entire LOD_Generator folder into scripts
    shutil.copytree(src, dst)

    # Create a Shelf button (optional, comment out if not desired)
    try:
        shelf_name = "CustomTools"  # name of the shelf to create the button on
        if not cmds.shelfLayout(shelf_name, exists=True):
            cmds.shelfLayout(shelf_name, parent="ShelfLayout")

        # If the button already exists, delete it
        existing_btns = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
        for btn in existing_btns:
            if cmds.shelfButton(btn, query=True, label=True) == "LOD Generator":
                cmds.deleteUI(btn)

        # Create the new button
        cmds.shelfButton(
            parent=shelf_name,
            command='import LOD_Generator.main; LOD_Generator.main.start()',
            image='commandButton.png',  # can change the icon
            label='LOD Generator',
            annotation='Open LOD Generator Tool',
            style='iconAndTextVertical'
        )
    except Exception as e:
        cmds.warning(f"Could not create shelf button: {e}")

    cmds.confirmDialog(title="Install Complete",
                       message="LOD Generator has been successfully installed!",
                       button=["OK"])


# When dragged into Maya, run automatically
install_tool()
