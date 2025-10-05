import maya.cmds as cmds # type: ignore

# WINDOW NAME
WINDOW_NAME = "LODGeneratorUI"

# Default LOD data
lod_data = [
    {"name": "LOD1", "percent": 50},
    {"name": "LOD2", "percent": 25},
    {"name": "LOD3", "percent": 10},
]

# Script job ID for selection tracking
selection_job_id = None
main_column_layout = None


def create_ui():
    """Create the main UI for the tool"""
    global selection_job_id, main_column_layout
    
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title="LOD Generator", sizeable=True, widthHeight=(300, 400))
    main_column_layout = cmds.columnLayout("main_column_layout", adjustableColumn=True, rowSpacing=10)

    cmds.text(label="LOD Settings - NguyenNP", align="center", height=20)

    # === TRIANGLE COUNT PREVIEW ===
    cmds.separator(height=5, style="in")
    cmds.rowLayout(numberOfColumns=1, adjustableColumn=1)
    cmds.text("original_tris", label="Original Triangles: ---", align="center", font="boldLabelFont")
    cmds.setParent(main_column_layout)
    cmds.separator(height=5, style="in")

    # === LOD LIST WITH SCROLL (so it doesn't push buttons off screen) ===
    cmds.scrollLayout("lod_scroll", childResizable=True, height=200)
    cmds.columnLayout("lod_column", adjustableColumn=True, rowSpacing=5)
    _draw_lod_items()
    cmds.setParent(main_column_layout)
    cmds.setParent(main_column_layout)

    cmds.separator(height=10, style="none")

    # Add / Remove buttons (full width like Generate button)
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach=[(1, "both", 2), (2, "both", 2)], columnWidth2=(145, 145))
    cmds.button(label="Add LOD", command=lambda x: add_lod())
    cmds.button(label="Remove LOD", command=lambda x: remove_lod())
    cmds.setParent(main_column_layout)

    cmds.separator(height=10, style="none")

    # === PROGRESS BAR ===
    cmds.progressBar("lod_progress_bar", width=280, height=20, visible=False)
    cmds.text("progress_text", label="", align="center", height=20, visible=False)

    cmds.separator(height=5, style="none")

    # Generate LODs button
    cmds.button(label="Generate LODs", height=40, backgroundColor=(0.3, 0.6, 0.3),
                command=lambda x: generate_lods())

    cmds.showWindow(WINDOW_NAME)
    
    # Create script job to auto-update on selection change
    selection_job_id = cmds.scriptJob(event=["SelectionChanged", update_preview], parent=WINDOW_NAME)
    
    # Initial preview update
    update_preview()


def _draw_lod_items():
    """Draw the LOD item list with triangle preview"""
    for i, lod in enumerate(lod_data):
        cmds.rowLayout(
            numberOfColumns=4,
            adjustableColumn=2,
            columnWidth4=(50, 120, 50, 80),
            columnAlign4=("center", "center", "center", "left"),
            parent="lod_column"
        )
        cmds.text(label=lod["name"])
        cmds.floatField(value=lod["percent"], minValue=0, maxValue=100, precision=1,
                        changeCommand=lambda val, idx=i: _update_percent(idx, val))
        cmds.text(label="%")
        cmds.text(f"lod_preview_{i}", label="---", align="left", font="plainLabelFont")
        cmds.setParent("lod_column")


def _update_percent(index, value):
    """Update percent when the user changes it"""
    lod_data[index]["percent"] = value
    update_preview()  # Auto refresh preview


def refresh_lod_list():
    """Redraw the list when adding/removing"""
    global main_column_layout
    
    # Clear all children from lod_column instead of deleting it
    if cmds.columnLayout("lod_column", exists=True):
        children = cmds.columnLayout("lod_column", query=True, childArray=True)
        if children:
            for child in children:
                cmds.deleteUI(child)
    
    # Redraw items in the existing column
    _draw_lod_items()


def add_lod():
    """Add a new LOD"""
    new_id = len(lod_data) + 1
    
    # New LOD percent is half of the last LOD
    last_percent = lod_data[-1]["percent"] if lod_data else 10
    new_percent = last_percent / 2.0
    
    lod_data.append({"name": f"LOD{new_id}", "percent": new_percent})
    refresh_lod_list()
    update_preview()


def remove_lod():
    """Remove the last LOD"""
    if len(lod_data) > 1:
        lod_data.pop()
        refresh_lod_list()
        update_preview()


def update_preview():
    """Update the triangle count preview based on current selection"""
    if not cmds.text("original_tris", exists=True):
        return
    
    selection = cmds.ls(sl=True, long=True, type="transform")
    
    if not selection:
        cmds.text("original_tris", edit=True, label="Original Triangles: ---")
        _clear_lod_preview()
        return
    
    # Get first selected mesh
    mesh = selection[0]
    shapes = cmds.listRelatives(mesh, shapes=True, noIntermediate=True, fullPath=True)
    
    if not shapes or cmds.nodeType(shapes[0]) != "mesh":
        cmds.text("original_tris", edit=True, label="Original Triangles: ---")
        _clear_lod_preview()
        return
    
    # Get triangle count
    try:
        tri_count = cmds.polyEvaluate(mesh, triangle=True)
        cmds.text("original_tris", edit=True, label=f"Original Triangles: {tri_count:,}")
        
        # Update LOD predictions
        _update_lod_preview(tri_count)
        
    except Exception as e:
        cmds.text("original_tris", edit=True, label="Original Triangles: ---")
        _clear_lod_preview()


def _clear_lod_preview():
    """Clear LOD preview texts"""
    for i in range(len(lod_data)):
        preview_text = f"lod_preview_{i}"
        if cmds.text(preview_text, exists=True):
            cmds.text(preview_text, edit=True, label="---")


def _update_lod_preview(original_tris):
    """Update the predicted triangle counts for each LOD"""
    for i, lod in enumerate(lod_data):
        preview_text = f"lod_preview_{i}"
        if cmds.text(preview_text, exists=True):
            percent = lod["percent"]
            predicted_tris = int(original_tris * (percent / 100.0))
            cmds.text(preview_text, edit=True, label=f"≈ {predicted_tris:,} tris")


def show_progress(current, total, mesh_name):
    """Update progress bar and status text"""
    if cmds.progressBar("lod_progress_bar", exists=True):
        cmds.progressBar("lod_progress_bar", edit=True, visible=True)
        cmds.text("progress_text", edit=True, visible=True)
        
        progress = int((current / float(total)) * 100)
        cmds.progressBar("lod_progress_bar", edit=True, progress=progress)
        cmds.text("progress_text", edit=True, 
                 label=f"Processing: {mesh_name} ({current}/{total})")
        cmds.refresh()  # Force UI update


def hide_progress():
    """Hide progress bar and status text"""
    if cmds.progressBar("lod_progress_bar", exists=True):
        cmds.progressBar("lod_progress_bar", edit=True, visible=False, progress=0)
        cmds.text("progress_text", edit=True, visible=False, label="")


def generate_lods():
    """Generate LODs with progress feedback"""
    from . import generator
    
    selection = cmds.ls(sl=True, long=True, type="transform")
    if not selection:
        cmds.warning("No mesh selected.")
        return
    
    total_meshes = len(selection)
    
    try:
        for i, mesh in enumerate(selection, 1):
            short_name = mesh.split("|")[-1]
            show_progress(i, total_meshes, short_name)
            generator.generate_lods_single(mesh, lod_data)
        
        cmds.text("progress_text", edit=True, 
                 label=f"✓ Completed! Generated LODs for {total_meshes} mesh(es)")
        cmds.refresh()
        
        # Hide progress after 2 seconds
        cmds.evalDeferred(hide_progress, lowestPriority=True)
        
    except Exception as e:
        hide_progress()
        cmds.error(f"LOD generation failed: {e}")