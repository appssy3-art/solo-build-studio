import bpy
import math
from mathutils import Vector, Euler

BLEND_FILE = r"E:\ai랩\AI자율회사만들기\solo_build_cliffside_drone_13s.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

scene = bpy.context.scene
col_int = bpy.data.collections.get("04_Interior_Workspace") or scene.collection

# Fireplace center
fx = 0.95
fy = 0.16 # Bring slightly forward
fz_floor = 0.15

# Remove any old / blocking fireplace parts
to_remove = [
    "1F_Lounge_FireboxRecess", "FireGlass_FrontGuard", 
    "1F_Lounge_FireplaceSurround", "1F_Lounge_FireplaceHearthBench",
    "1F_Lounge_FireEmbersBed"
]
for name in list(bpy.data.objects.keys()):
    if name in to_remove or name.startswith("FlameTongue_") or name.startswith("FireLog_"):
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

# -------------------------------------------------------------
# 1. ARCHITECTURAL SURROUND (Feature Wall Backdrop)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(fx, fy + 0.18, fz_floor + 1.25), rotation=(math.radians(90), 0, 0))
surround = bpy.context.active_object
surround.name = "1F_Lounge_FireplaceSurround"
surround.scale = (2.60, 1.80, 1.0) # 2.6m wide, 1.8m tall vertical plane

mat_surround = bpy.data.materials.get("Mat_FireplaceSurroundDarkSlate")
if not mat_surround:
    mat_surround = bpy.data.materials.new("Mat_FireplaceSurroundDarkSlate")
bsdf_sur = mat_surround.node_tree.nodes.get("Principled BSDF")
if bsdf_sur:
    bsdf_sur.inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1.0)
    bsdf_sur.inputs["Roughness"].default_value = 0.6
surround.data.materials.clear()
surround.data.materials.append(mat_surround)
col_int.objects.link(surround)
scene.collection.objects.unlink(surround)

# -------------------------------------------------------------
# 2. OPEN FIREPLACE NICHE (Hollow Cavity: Back, Top, Bottom, Sides)
# -------------------------------------------------------------
# Niche Backplate (Jet black steel cavity back)
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(fx, fy + 0.15, fz_floor + 0.85), rotation=(math.radians(90), 0, 0))
backplate = bpy.context.active_object
backplate.name = "1F_Lounge_NicheBack"
backplate.scale = (2.10, 0.75, 1.0)

mat_black = bpy.data.materials.get("Mat_FireboxBlackIron")
if not mat_black:
    mat_black = bpy.data.materials.new("Mat_FireboxBlackIron")
bsdf_black = mat_black.node_tree.nodes.get("Principled BSDF")
if bsdf_black:
    bsdf_black.inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1.0)
    bsdf_black.inputs["Roughness"].default_value = 0.95
backplate.data.materials.append(mat_black)
col_int.objects.link(backplate)
scene.collection.objects.unlink(backplate)

# Niche Top Hood / Ceiling
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(fx, fy + 0.05, fz_floor + 1.22), rotation=(0, 0, 0))
hood = bpy.context.active_object
hood.name = "1F_Lounge_NicheTop"
hood.scale = (2.10, 0.22, 1.0)
hood.data.materials.append(mat_black)
col_int.objects.link(hood)
scene.collection.objects.unlink(hood)

# Hearth Bench (Low Floating Stone Shelf)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy - 0.08, fz_floor + 0.28))
hearth = bpy.context.active_object
hearth.name = "1F_Lounge_FireplaceHearthBench"
hearth.scale = (2.70, 0.55, 0.24)
mat_hearth = bpy.data.materials.get("Mat_FireHearthTravertine")
hearth.data.materials.append(mat_hearth)
col_int.objects.link(hearth)
scene.collection.objects.unlink(hearth)

# Niche Floor / Ember tray
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy + 0.02, fz_floor + 0.48))
tray = bpy.context.active_object
tray.name = "1F_Lounge_FireEmbersBed"
tray.scale = (2.00, 0.24, 0.08)

# Glowing Embers Material (Rich pulsing orange-red emission)
mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")
bsdf_emb = mat_ember.node_tree.nodes.get("Principled BSDF")
if bsdf_emb:
    bsdf_emb.inputs["Base Color"].default_value = (0.02, 0.005, 0.0, 1.0)
    if "Emission Color" in bsdf_emb.inputs:
        bsdf_emb.inputs["Emission Color"].default_value = (1.0, 0.25, 0.02, 1.0)
        bsdf_emb.inputs["Emission Strength"].default_value = 60.0
tray.data.materials.append(mat_ember)
col_int.objects.link(tray)
scene.collection.objects.unlink(tray)

# -------------------------------------------------------------
# 3. CERAMIC FIREPLACE LOGS
# -------------------------------------------------------------
mat_log = bpy.data.materials.get("Mat_FirewoodCharred")
log_configs = [
    # (dx, dy, dz, length, rad, rx, ry, rz)
    (-0.65, 0.01, 0.54, 0.65, 0.055, 0, 85, 12),
    (-0.15, 0.02, 0.55, 0.70, 0.060, 0, 92, -8),
    ( 0.45, 0.01, 0.54, 0.65, 0.055, 0, 88, 15),
    ( 0.75, 0.00, 0.53, 0.50, 0.050, 0, 90, -10),
    # Diagonal crossing logs
    (-0.40, -0.02, 0.62, 0.55, 0.045, 18, 65, 25),
    ( 0.20, -0.02, 0.63, 0.60, 0.048, -15, 110, -20),
]
for i, (dx, dy, dz, length, rad, rx, ry, rz) in enumerate(log_configs):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=rad, depth=length, 
        location=(fx + dx, fy + dy, fz_floor + dz),
        rotation=(math.radians(rx), math.radians(ry), math.radians(rz))
    )
    log_obj = bpy.context.active_object
    log_obj.name = f"FireLog_{i}"
    log_obj.data.materials.append(mat_log)
    col_int.objects.link(log_obj)
    scene.collection.objects.unlink(log_obj)

# -------------------------------------------------------------
# 4. ROARING VIBRANT FLAME TONGUES (Front & Center!)
# -------------------------------------------------------------
# Materials for flames
mat_flame_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
bsdf_fc = mat_flame_core.node_tree.nodes.get("Principled BSDF")
if bsdf_fc:
    bsdf_fc.inputs["Base Color"].default_value = (0, 0, 0, 1) # Pure black base so daylight doesn't wash it out
    if "Emission Color" in bsdf_fc.inputs:
        bsdf_fc.inputs["Emission Color"].default_value = (1.0, 0.95, 0.55, 1.0)
        bsdf_fc.inputs["Emission Strength"].default_value = 140.0

mat_flame_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
bsdf_fo = mat_flame_outer.node_tree.nodes.get("Principled BSDF")
if bsdf_fo:
    bsdf_fo.inputs["Base Color"].default_value = (0, 0, 0, 1)
    if "Emission Color" in bsdf_fo.inputs:
        bsdf_fo.inputs["Emission Color"].default_value = (1.0, 0.40, 0.02, 1.0)
        bsdf_fo.inputs["Emission Strength"].default_value = 110.0

# Create 14 flame tongues across the 1.9m opening!
# Flame heights between 0.35m and 0.62m!
flame_data = [
    (-0.85, 0.00, 0.52, 0.09, 0.40, -8, mat_flame_outer),
    (-0.70, 0.01, 0.53, 0.11, 0.50,  5, mat_flame_core),
    (-0.55, -0.01, 0.52, 0.10, 0.45, -4, mat_flame_outer),
    (-0.40, 0.01, 0.54, 0.13, 0.58,  6, mat_flame_core),
    (-0.25, 0.00, 0.53, 0.12, 0.52, -5, mat_flame_outer),
    (-0.10, 0.01, 0.55, 0.14, 0.62,  4, mat_flame_core),
    ( 0.05, 0.00, 0.54, 0.13, 0.58, -6, mat_flame_outer),
    ( 0.20, 0.01, 0.55, 0.14, 0.60,  5, mat_flame_core),
    ( 0.35, -0.01, 0.53, 0.12, 0.53, -4, mat_flame_outer),
    ( 0.50, 0.01, 0.54, 0.13, 0.56,  6, mat_flame_core),
    ( 0.65, 0.00, 0.52, 0.11, 0.48, -5, mat_flame_outer),
    ( 0.80, 0.01, 0.51, 0.09, 0.42,  7, mat_flame_core),
]

for i, (dx, dy, dz, r1, h, ry, mat) in enumerate(flame_data):
    bpy.ops.mesh.primitive_cone_add(
        radius1=r1, radius2=0.004, depth=h,
        location=(fx + dx, fy + dy, fz_floor + dz + h * 0.5),
        rotation=(0, math.radians(ry), 0)
    )
    ft = bpy.context.active_object
    ft.name = f"FlameTongue_{i}"
    ft.scale = (1.5, 0.35, 1.0)
    ft.data.materials.append(mat)
    col_int.objects.link(ft)
    scene.collection.objects.unlink(ft)

# -------------------------------------------------------------
# 5. DEDICATED FIREPLACE LIGHTS
# -------------------------------------------------------------
lfire1 = bpy.data.objects.get("Light_1F_FireplacePointGlow")
if lfire1:
    lfire1.location = (fx, fy - 0.18, fz_floor + 0.80)
    lfire1.data.energy = 1100.0
    lfire1.data.color = (1.0, 0.45, 0.08)

lfire2 = bpy.data.objects.get("Light_1F_FireplaceSpotDown")
if lfire2:
    lfire2.location = (fx, fy - 0.45, fz_floor + 1.05)
    lfire2.data.energy = 550.0
    lfire2.data.color = (1.0, 0.58, 0.15)

# Save mainfile
bpy.ops.wm.save_mainfile()
print("MAINFILE_SAVED_WITH_OPEN_FIREPLACE")

# Render frame 220 in Sunset lighting to verify
scene.frame_set(220)
test_out = r"E:\ai랩\AI자율회사만들기\scratch\test_fireplace_open_f220.png"
scene.render.filepath = test_out
bpy.ops.render.render(write_still=True)
print("TEST_OPEN_FIREPLACE_RENDERED:", test_out)

