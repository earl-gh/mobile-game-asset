# Run inside Blender. Exports one asset collection to a Unity-ready FBX
# (scale 1, rotation 0, +Y up, Blender -Y front -> Unity +Z forward). Settings explained in references/unity.md.
import bpy, os

COLLECTION = "SM_Asset"      # collection holding the asset's meshes, LODs, _COL, SOCKET_ empties, armature
OUT_DIR = "//export"

col = bpy.data.collections[COLLECTION]
objs = [o for o in col.all_objects if o.type in {'MESH', 'ARMATURE', 'EMPTY'}]
warn = [o.name for o in objs if o.type == 'MESH' and o.modifiers and o.modifiers[-1].type != 'TRIANGULATE']
if warn:
    print("WARN no Triangulate modifier last on:", ", ".join(warn))

bpy.ops.object.select_all(action='DESELECT')
for o in objs:
    o.hide_set(False)
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]

path = os.path.join(bpy.path.abspath(OUT_DIR), f"{COLLECTION}.fbx")
os.makedirs(os.path.dirname(path), exist_ok=True)
# bake_space_transform is flagged experimental and can break armatures and animation, so static assets only
has_armature = any(o.type == 'ARMATURE' for o in objs)
bpy.ops.export_scene.fbx(
    filepath=path, use_selection=True, object_types={'MESH', 'ARMATURE', 'EMPTY'},
    apply_scale_options='FBX_SCALE_ALL', bake_space_transform=not has_armature,
    axis_forward='-Z', axis_up='Y',
    use_mesh_modifiers=True, mesh_smooth_type='FACE', use_tspace=True,
    colors_type='LINEAR',                 # skin mask in vertex colour R must arrive exactly 0/1
    add_leaf_bones=False, use_armature_deform_only=True, bake_anim=False,
    path_mode='STRIP')    # textures are imported separately in Unity
print(f"EXPORTED {len(objs)} objects -> {path}")
