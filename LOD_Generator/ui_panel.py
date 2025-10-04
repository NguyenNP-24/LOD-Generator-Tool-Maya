import maya.cmds as cmds # type: ignore

# WINDOW NAME
WINDOW_NAME = "LODGeneratorUI"

# Default LOD data
lod_data = [
    {"name": "LOD1", "percent": 50},
    {"name": "LOD2", "percent": 25},
    {"name": "LOD3", "percent": 10},
]


def create_ui():
    """Create the main UI for the tool"""
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title="LOD Generator", sizeable=False, widthHeight=(300, 350))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.text(label="LOD Settings - NguyenNP", align="center", height=20)

    # Container for LOD list
    cmds.frameLayout(labelVisible=False, collapsable=False, borderVisible=False)
    cmds.columnLayout("lod_column", adjustableColumn=True, rowSpacing=5)
    _draw_lod_items()
    cmds.setParent("..")
    cmds.setParent("..")
    
    # Add / Remove buttons
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(145, 145), columnAlign2=("center", "center"))
    cmds.button(label="Add LOD", command=lambda x: add_lod())
    cmds.button(label="Remove LOD", command=lambda x: remove_lod())
    cmds.setParent("..")

    cmds.separator(height=10, style="none")

    # Generate LODs button
    cmds.button(label="Generate LODs", height=40, backgroundColor=(0.3, 0.6, 0.3),
                command=lambda x: generate_lods())

    cmds.showWindow(WINDOW_NAME)


def _draw_lod_items():
    """Draw the LOD item list"""
    for i, lod in enumerate(lod_data):
        cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=2,
            columnWidth3=(50, 180, 50),
            columnAlign3=("center", "center", "center"),
        )
        cmds.text(label=lod["name"])
        cmds.floatField(value=lod["percent"], minValue=0, maxValue=100, precision=1,
                        changeCommand=lambda val, idx=i: _update_percent(idx, val))
        cmds.text(label="%")
        cmds.setParent("..")

def _update_percent(index, value):
    """Update percent when the user changes it"""
    lod_data[index]["percent"] = value

def refresh_lod_list():
    """Redraw the list when adding/removing"""
    if cmds.columnLayout("lod_column", exists=True):
        cmds.deleteUI("lod_column")
        cmds.columnLayout("lod_column", adjustableColumn=True, rowSpacing=5, parent=WINDOW_NAME)
        _draw_lod_items()

def add_lod():
    """Add a new LOD with default values"""
    new_id = len(lod_data) + 1
    lod_data.append({"name": f"LOD{new_id}", "percent": 5})
    if cmds.columnLayout("lod_column", exists=True):
        parent = cmds.columnLayout("lod_column", query=True, parent=True)
        cmds.deleteUI("lod_column")
        cmds.columnLayout("lod_column", adjustableColumn=True, rowSpacing=5, parent=parent)
        _draw_lod_items()

def remove_lod():
    """Remove the last LOD"""
    if len(lod_data) > 1:
        lod_data.pop()
        cmds.deleteUI("lod_column")
        cmds.columnLayout("lod_column", adjustableColumn=True, rowSpacing=5, parent=WINDOW_NAME)
        _draw_lod_items()

def generate_lods():
    """Placeholder for the actual generate function"""
    from . import generator
    generator.generate_lods(lod_data)


