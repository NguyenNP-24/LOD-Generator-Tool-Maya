import maya.cmds as cmds # type: ignore
import maya.mel as mel # type: ignore   # For _cleanup_nonmanifold. cmds doesn't have polyCleanup 

def generate_lods(lod_percents):
    """Generate LODs for the selected meshes"""
    selection = cmds.ls(sl=True, long=True, type="transform")
    if not selection:
        cmds.warning("No mesh selected.")
        return

    for mesh in selection:
        # print(f"\n--- Generating LODs for: {mesh} ---")

        # create group containing LODs
        group_name = f"{mesh}_LODs"
        if not cmds.objExists(group_name):
            group_name = cmds.group(empty=True, name=group_name)
            parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
            if parent:
                try:
                    cmds.parent(group_name, parent[0])
                except RuntimeError as e:
                    cmds.warning(f"Cannot parent {group_name} to {parent[0]}: {e}")

        # find original skinCluster if any
        skin_cluster = _find_skincluster(mesh)

        # create LODs
        for i, lod_info in enumerate(lod_percents, 1):
            percent = lod_info["percent"]
            lod_name = lod_info["name"]

            lod_mesh = cmds.duplicate(mesh, name=f"{mesh}_{lod_name}")[0]

            _cleanup_nonmanifold(lod_mesh)
            _apply_poly_reduce(lod_mesh, percent)

            # delete history (to remove polyReduce node, clean mesh)
            cmds.delete(lod_mesh, ch=True)
            
            # copy skin weights if present
            if skin_cluster:
                _copy_skin_weights(skin_cluster, mesh, lod_mesh)

            # parent into group
            cmds.parent(lod_mesh, group_name)

            # add to display layer
            _assign_display_layer(lod_mesh, lod_name)
            # print(f"✅ Created {lod_name} ({percent}%)")


# =============================
# HELPER FUNCTIONS
# =============================

def _find_skincluster(mesh):
    """Find the skinCluster of the mesh (if any)"""
    history = cmds.listHistory(mesh) or []
    for node in history:
        if cmds.nodeType(node) == "skinCluster":
            return node
    return None

def _cleanup_nonmanifold(mesh):
    """Clean up non-manifold geometry"""
    try:
        cmds.select(mesh)
        mel.eval('polyCleanupArgList 3 { "0","2","1","0","0","1","0","1","0","0","0","0","0","1" };')
        cmds.select(clear=True)
        # print(f"Cleaned non-manifold: {mesh}")
    except Exception as e:
        cmds.warning(f"Cleanup failed on {mesh}: {e}")

def _apply_poly_reduce(mesh, percent):
    """Reduce polygons using built-in tool"""
    # Check if mesh has faces
    face_count = cmds.polyEvaluate(mesh, face=True)
    if face_count == 0:
        cmds.warning(f"{mesh} has no faces to reduce.")
        return    
    try:
        cmds.polyReduce(
            mesh,
            version=1,
            termination=0,
            percentage=100 - percent,  # 100 - percent because Maya calculates the percentage to keep
            keepQuadsWeight=0.5,
            keepColorBorder=True,
            keepFaceGroupBorder=True,
            keepHardEdge=True,
            keepCreaseEdge=True,
            keepBorder=True,
            keepMapBorder=True,
            useVirtualSymmetry=False,
            cachingReduce=True,
            preserveTopology=True,
        )
        # print(f"Reduced {mesh} → {percent}%")
    except Exception as e:
        cmds.warning(f"PolyReduce failed on {mesh}: {e}")

def _copy_skin_weights(source_skin, source_mesh, target_mesh):
    """Copy skin weights from source mesh to new LOD"""
    try:
        joints = cmds.skinCluster(source_skin, query=True, influence=True)
        if not joints:
            return

        new_skin = cmds.skinCluster(joints, target_mesh, toSelectedBones=True, normalizeWeights=1)[0]
        cmds.copySkinWeights(
            sourceSkin=source_skin,
            destinationSkin=new_skin,
            noMirror=True,
            surfaceAssociation="closestPoint",
            influenceAssociation=["closestJoint", "closestBone", "oneToOne"],
        )
        # print(f"Copied skin weights → {target_mesh}")
    except Exception as e:
        cmds.warning(f"Copy skin weights failed for {target_mesh}: {e}")

def _assign_display_layer(mesh, lod_name):
    """Add mesh to display layer according to LOD level."""
    if not cmds.objExists(lod_name):
        cmds.createDisplayLayer(name=lod_name, number=1, empty=True)
    cmds.editDisplayLayerMembers(lod_name, mesh, noRecurse=True)
    cmds.setAttr(f"{lod_name}.visibility", 0)  # Hide layer by default