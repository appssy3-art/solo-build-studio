import bpy
import math
from mathutils import Vector, Euler

# Open mainfile
BLEND_FILE = r"E:\ai랩\AI자율회사만들기\solo_build_cliffside_drone_13s.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

scene = bpy.context.scene
col_int = bpy.data.collections.get("04_Interior_Workspace") or scene.collection

# Center coordinates for 1F luxury fireplace:
# Located between mullion 0.0 and 2.2 -> center at X = 1.05
# Y = 0.25 (against the slat feature wall)
fx = 0.95
fy = 0.22
fz_floor = 0.15 # 1F floor height

# Clean up any previous test objects
cleanup_names = [
    "1F_Lounge_FireplaceSurround", "1F_Lounge_FireplaceHearthBench", 
    "1F_Lounge_FireboxRecess", "1F_Lounge_FireFlameGlow", 
    "1F_Lounge_FireTopWarmStrip", "1F_Lounge_FireEmbersBed",
    "Light_1F_FireplacePointGlow", "Light_1F_FireplaceSpotDown"
]
for name in list(bpy.data.objects.keys()):
    if name in cleanup_names or name.startswith("FireLog_") or name.startswith("FlameTongue_") or name.startswith("FireGlass_"):
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

# -------------------------------------------------------------
# 1. LUXURY ARCHITECTURAL CHIMNEY BREAST / SURROUND
# -------------------------------------------------------------
# Dark charcoal slate / brushed titanium frame that clearly defines the fireplace zone
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy + 0.12, fz_floor + 1.15))
surround = bpy.context.active_object
surround.name = "1F_Lounge_FireplaceSurround"
surround.scale = (2.60, 0.24, 1.90)

mat_surround = bpy.data.materials.get("Mat_FireplaceSurroundDarkSlate")
if not mat_surround:
    mat_surround = bpy.data.materials.new("Mat_FireplaceSurroundDarkSlate")
    mat_surround.use_nodes = True
bsdf_sur = mat_surround.node_tree.nodes.get("Principled BSDF")
if bsdf_sur:
    bsdf_sur.inputs["Base Color"].default_value = (0.04, 0.04, 0.045, 1.0)
    bsdf_sur.inputs["Roughness"].default_value = 0.40
    if "Metallic" in bsdf_sur.inputs:
        bsdf_sur.inputs["Metallic"].default_value = 0.20
surround.data.materials.clear()
surround.data.materials.append(mat_surround)
if surround.name not in col_int.objects:
    col_int.objects.link(surround)
    scene.collection.objects.unlink(surround)

# -------------------------------------------------------------
# 2. FIREBOX RECESS (Matte Deep Black Cavity)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy + 0.02, fz_floor + 0.85))
firebox = bpy.context.active_object
firebox.name = "1F_Lounge_FireboxRecess"
firebox.scale = (2.20, 0.26, 0.72)

mat_box = bpy.data.materials.get("Mat_FireboxBlackIron")
if not mat_box:
    mat_box = bpy.data.materials.new("Mat_FireboxBlackIron")
    mat_box.use_nodes = True
bsdf_box = mat_box.node_tree.nodes.get("Principled BSDF")
if bsdf_box:
    bsdf_box.inputs["Base Color"].default_value = (0.015, 0.015, 0.015, 1.0)
    bsdf_box.inputs["Roughness"].default_value = 0.90
firebox.data.materials.clear()
firebox.data.materials.append(mat_box)
if firebox.name not in col_int.objects:
    col_int.objects.link(firebox)
    scene.collection.objects.unlink(firebox)

# -------------------------------------------------------------
# 3. HEARTH BENCH (Floating Italian Travertine/Marble base)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy - 0.08, fz_floor + 0.24))
hearth = bpy.context.active_object
hearth.name = "1F_Lounge_FireplaceHearthBench"
hearth.scale = (2.80, 0.55, 0.22)

mat_hearth = bpy.data.materials.get("Mat_FireHearthTravertine")
if not mat_hearth:
    mat_hearth = bpy.data.materials.new("Mat_FireHearthTravertine")
    mat_hearth.use_nodes = True
bsdf_h = mat_hearth.node_tree.nodes.get("Principled BSDF")
if bsdf_h:
    bsdf_h.inputs["Base Color"].default_value = (0.28, 0.25, 0.22, 1.0)
    bsdf_h.inputs["Roughness"].default_value = 0.35
hearth.data.materials.clear()
hearth.data.materials.append(mat_hearth)
if hearth.name not in col_int.objects:
    col_int.objects.link(hearth)
    scene.collection.objects.unlink(hearth)

# -------------------------------------------------------------
# 4. GLOWING COALS / CHARCOAL BED (Under the logs)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy - 0.02, fz_floor + 0.52))
bed = bpy.context.active_object
bed.name = "1F_Lounge_FireEmbersBed"
bed.scale = (2.05, 0.20, 0.08)

mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")
if not mat_ember:
    mat_ember = bpy.data.materials.new("Mat_FireEmbersGlow")
    mat_ember.use_nodes = True
bsdf_emb = mat_ember.node_tree.nodes.get("Principled BSDF")
if bsdf_emb:
    bsdf_emb.inputs["Base Color"].default_value = (0.05, 0.01, 0.0, 1.0)
    if "Emission Color" in bsdf_emb.inputs:
        bsdf_emb.inputs["Emission Color"].default_value = (1.0, 0.22, 0.02, 1.0)
        bsdf_emb.inputs["Emission Strength"].default_value = 45.0
bed.data.materials.clear()
bed.data.materials.append(mat_ember)
if bed.name not in col_int.objects:
    col_int.objects.link(bed)
    scene.collection.objects.unlink(bed)

# -------------------------------------------------------------
# 5. CERAMIC FIREPLACE LOGS (Birch / Oak Wood Stack)
# -------------------------------------------------------------
mat_log = bpy.data.materials.get("Mat_FirewoodCharred")
if not mat_log:
    mat_log = bpy.data.materials.new("Mat_FirewoodCharred")
    mat_log.use_nodes = True
bsdf_log = mat_log.node_tree.nodes.get("Principled BSDF")
if bsdf_log:
    bsdf_log.inputs["Base Color"].default_value = (0.08, 0.04, 0.02, 1.0)
    bsdf_log.inputs["Roughness"].default_value = 0.85

log_configs = [
    # (dx, dy, dz, length, radius, rot_x, rot_y, rot_z)
    (-0.65, -0.02, 0.58, 0.70, 0.055, 0, 85, 12),
    (-0.15, -0.01, 0.60, 0.75, 0.060, 0, 92, -10),
    ( 0.45, -0.02, 0.58, 0.68, 0.055, 0, 88, 15),
    ( 0.75, -0.03, 0.57, 0.55, 0.050, 0, 90, -8),
    # Diagonal crossing logs
    (-0.40, -0.04, 0.67, 0.60, 0.045, 15, 65, 25),
    ( 0.20, -0.04, 0.68, 0.65, 0.048, -12, 110, -20),
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
    if log_obj.name not in col_int.objects:
        col_int.objects.link(log_obj)
        scene.collection.objects.unlink(log_obj)

# -------------------------------------------------------------
# 6. DYNAMIC FLAME TONGUES (Multiple Tapered Glowing Fire Blades)
# -------------------------------------------------------------
# Distinct organic flame tongue shapes reaching high up
mat_flame_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
if not mat_flame_core:
    mat_flame_core = bpy.data.materials.new("Mat_FlameCoreWhiteYellow")
    mat_flame_core.use_nodes = True
bsdf_fc = mat_flame_core.node_tree.nodes.get("Principled BSDF")
if bsdf_fc:
    if "Emission Color" in bsdf_fc.inputs:
        bsdf_fc.inputs["Emission Color"].default_value = (1.0, 0.90, 0.45, 1.0)
        bsdf_fc.inputs["Emission Strength"].default_value = 95.0

mat_flame_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
if not mat_flame_outer:
    mat_flame_outer = bpy.data.materials.new("Mat_FlameOuterVividOrange")
    mat_flame_outer.use_nodes = True
bsdf_fo = mat_flame_outer.node_tree.nodes.get("Principled BSDF")
if bsdf_fo:
    if "Emission Color" in bsdf_fo.inputs:
        bsdf_fo.inputs["Emission Color"].default_value = (1.0, 0.38, 0.02, 1.0)
        bsdf_fo.inputs["Emission Strength"].default_value = 80.0

# Create 11 flame cones/tongues along the firebox length
flame_positions = [
    # (dx, dy, dz, r1, height, rot_y, mat)
    (-0.80, -0.02, 0.60, 0.07, 0.38, -6, mat_flame_outer),
    (-0.62, -0.01, 0.62, 0.09, 0.48,  4, mat_flame_core),
    (-0.45, -0.03, 0.60, 0.08, 0.42, -3, mat_flame_outer),
    (-0.28, -0.01, 0.64, 0.10, 0.56,  5, mat_flame_core),
    (-0.10, -0.02, 0.62, 0.09, 0.50, -4, mat_flame_outer),
    ( 0.08, -0.01, 0.65, 0.11, 0.60,  3, mat_flame_core),  # Center tall flame
    ( 0.26, -0.02, 0.63, 0.10, 0.54, -5, mat_flame_core),
    ( 0.44, -0.01, 0.61, 0.09, 0.46,  6, mat_flame_outer),
    ( 0.62, -0.03, 0.60, 0.08, 0.44, -4, mat_flame_core),
    ( 0.78, -0.01, 0.58, 0.07, 0.36,  5, mat_flame_outer),
]

for i, (dx, dy, dz, r1, h, ry, mat) in enumerate(flame_positions):
    # Cone representing flame tongue
    bpy.ops.mesh.primitive_cone_add(
        radius1=r1, radius2=0.005, depth=h,
        location=(fx + dx, fy + dy, fz_floor + dz + h * 0.5),
        rotation=(0, math.radians(ry), 0)
    )
    ft = bpy.context.active_object
    ft.name = f"FlameTongue_{i}"
    # Flatten slightly in Y for ribbon fire effect
    ft.scale = (1.4, 0.45, 1.0)
    ft.data.materials.append(mat)
    if ft.name not in col_int.objects:
        col_int.objects.link(ft)
        scene.collection.objects.unlink(ft)

# -------------------------------------------------------------
# 7. TEMPERED PROTECTIVE GLASS SCREEN (Modern Linear Fireplace Screen)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy - 0.12, fz_floor + 0.78))
fglass = bpy.context.active_object
fglass.name = "FireGlass_FrontGuard"
fglass.scale = (2.10, 0.015, 0.45)

mat_fglass = bpy.data.materials.get("Mat_FireGlassTempered")
if not mat_fglass:
    mat_fglass = bpy.data.materials.new("Mat_FireGlassTempered")
    mat_fglass.use_nodes = True
bsdf_fg = mat_fglass.node_tree.nodes.get("Principled BSDF")
if bsdf_fg:
    bsdf_fg.inputs["Roughness"].default_value = 0.05
    if "Transmission Weight" in bsdf_fg.inputs:
        bsdf_fg.inputs["Transmission Weight"].default_value = 0.92
    elif "Transmission" in bsdf_fg.inputs:
        bsdf_fg.inputs["Transmission"].default_value = 0.92
fglass.data.materials.clear()
fglass.data.materials.append(mat_fglass)
if fglass.name not in col_int.objects:
    col_int.objects.link(fglass)
    scene.collection.objects.unlink(fglass)

# -------------------------------------------------------------
# 8. INTENSE FIREPLACE LIGHTS
# -------------------------------------------------------------
# Point light 1: Center hearth glow (warm radiant fire)
ldata1 = bpy.data.lights.new(name="Light_1F_FireplacePointGlow", type='POINT')
ldata1.energy = 850.0 # High energy to clearly wash the room
ldata1.color = (1.0, 0.44, 0.08)
ldata1.shadow_soft_size = 0.5
ldata1.use_shadow = True
lobj1 = bpy.data.objects.new(name="Light_1F_FireplacePointGlow", object_data=ldata1)
lobj1.location = (fx, fy - 0.15, fz_floor + 0.85)
col_int.objects.link(lobj1)

# Point light 2: Wider ambient fill
ldata2 = bpy.data.lights.new(name="Light_1F_FireplaceSpotDown", type='POINT')
ldata2.energy = 450.0
ldata2.color = (1.0, 0.60, 0.20)
ldata2.shadow_soft_size = 0.8
ldata2.use_shadow = False
lobj2 = bpy.data.objects.new(name="Light_1F_FireplaceSpotDown", object_data=ldata2)
lobj2.location = (fx, fy - 0.50, fz_floor + 1.10)
col_int.objects.link(lobj2)

# Save blend file
bpy.ops.wm.save_mainfile()
print("FIREPLACE_REBUILT_AND_SAVED")

# Render frame 220 to inspect the difference!
scene.frame_set(220)
test_out = r"E:\ai랩\AI자율회사만들기\scratch\test_fireplace_f220_v2.png"
scene.render.filepath = test_out
bpy.ops.render.render(write_still=True)
print("TEST_V2_RENDERED:", test_out)

