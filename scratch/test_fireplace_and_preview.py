import bpy
import math
import os
from mathutils import Vector, Euler

# 1. Load scene
BLEND_FILE = r"E:\ai랩\AI자율회사만들기\solo_build_cliffside_drone_13s.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

scene = bpy.context.scene
col_int = bpy.data.collections.get("04_Interior_Workspace") or scene.collection

# Fireplace target center:
# Located at X = 0.85 (between mullions 0.0 and 2.2, directly visible through front glass),
# Y = 0.15 (just behind the sofa/armchair area, with direct line of sight from drone camera)
fx, fy = 0.85, 0.15

# Get existing objects
sur = bpy.data.objects.get("1F_Lounge_FireplaceSurround")
hearth = bpy.data.objects.get("1F_Lounge_FireplaceHearthBench")
firebox = bpy.data.objects.get("1F_Lounge_FireboxRecess")
flame = bpy.data.objects.get("1F_Lounge_FireFlameGlow")
strip = bpy.data.objects.get("1F_Lounge_FireTopWarmStrip")

# Transform Surround wall (Rich charcoal fluted marble feature wall)
if sur:
    sur.location = (fx, fy + 0.15, 1.40)
    sur.scale = (2.30, 0.35, 2.30)

# Transform Hearth Bench (floating architectural stone bench)
if hearth:
    hearth.location = (fx, fy - 0.05, 0.52)
    hearth.scale = (2.50, 0.60, 0.40)

# Transform Firebox Recess (deep recessed black fire cavity)
if firebox:
    firebox.location = (fx, fy + 0.05, 1.05)
    firebox.scale = (1.95, 0.20, 0.65)

# Transform Flame Ribbon: make it MUCH taller and wider so it's unmistakable from outside!
if flame:
    flame.location = (fx, fy, 0.98)
    flame.scale = (1.80, 0.15, 0.48) # Height now ~0.5m!

# Transform warm strip
if strip:
    strip.location = (fx, fy - 0.02, 1.36)
    strip.scale = (1.90, 0.06, 0.06)

# Create glowing ember bed if not exists
ember = bpy.data.objects.get("1F_Lounge_FireEmbersBed")
if not ember:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy, 0.74))
    ember = bpy.context.active_object
    ember.name = "1F_Lounge_FireEmbersBed"
    ember.scale = (1.82, 0.16, 0.06)
    if ember.name not in col_int.objects:
        col_int.objects.link(ember)
        bpy.context.scene.collection.objects.unlink(ember)
else:
    ember.location = (fx, fy, 0.74)
    ember.scale = (1.82, 0.16, 0.06)

# Materials setup
# 1) Flame material: Super high emission with vivid fiery orange-yellow
mat_fire = bpy.data.materials.get("Mat_1F_FireplaceFlame")
if not mat_fire:
    mat_fire = bpy.data.materials.new("Mat_1F_FireplaceFlame")
    mat_fire.use_nodes = True
if flame:
    if flame.data.materials:
        flame.data.materials[0] = mat_fire
    else:
        flame.data.materials.append(mat_fire)

bsdf_fire = mat_fire.node_tree.nodes.get("Principled BSDF")
if bsdf_fire:
    if "Emission Color" in bsdf_fire.inputs:
        bsdf_fire.inputs["Emission Color"].default_value = (1.0, 0.40, 0.04, 1.0)
        bsdf_fire.inputs["Emission Strength"].default_value = 65.0
    elif "Emission" in bsdf_fire.inputs:
        bsdf_fire.inputs["Emission"].default_value = (1.0, 0.40, 0.04, 1.0)

# 2) Ember bed material: glowing deep red/orange coals
mat_ember = bpy.data.materials.get("Mat_1F_FireplaceEmbers")
if not mat_ember:
    mat_ember = bpy.data.materials.new("Mat_1F_FireplaceEmbers")
    mat_ember.use_nodes = True
if ember:
    if ember.data.materials:
        ember.data.materials[0] = mat_ember
    else:
        ember.data.materials.append(mat_ember)

bsdf_ember = mat_ember.node_tree.nodes.get("Principled BSDF")
if bsdf_ember:
    bsdf_ember.inputs["Base Color"].default_value = (0.05, 0.01, 0.0, 1.0)
    if "Emission Color" in bsdf_ember.inputs:
        bsdf_ember.inputs["Emission Color"].default_value = (1.0, 0.18, 0.02, 1.0)
        bsdf_ember.inputs["Emission Strength"].default_value = 35.0

# 3) Dedicated warm fireplace lights
# Light 1: Radial point light in the hearth
old_fire_light = bpy.data.objects.get("Light_1F_FireplacePointGlow")
if old_fire_light:
    bpy.data.objects.remove(old_fire_light, do_unlink=True)

ldata_fire = bpy.data.lights.new(name="Light_1F_FireplacePointGlow", type='POINT')
ldata_fire.energy = 550.0
ldata_fire.color = (1.0, 0.45, 0.10)
ldata_fire.shadow_soft_size = 0.40
ldata_fire.use_shadow = True
lobj_fire = bpy.data.objects.new(name="Light_1F_FireplacePointGlow", object_data=ldata_fire)
lobj_fire.location = (fx, fy - 0.20, 1.05)
col_int.objects.link(lobj_fire)

# Light 2: Downward spot light inside top of firebox
old_spot = bpy.data.objects.get("Light_1F_FireplaceSpotDown")
if old_spot:
    bpy.data.objects.remove(old_spot, do_unlink=True)

ldata_spot = bpy.data.lights.new(name="Light_1F_FireplaceSpotDown", type='SPOT')
ldata_spot.energy = 350.0
ldata_spot.color = (1.0, 0.60, 0.25)
ldata_spot.spot_size = math.radians(75)
ldata_spot.spot_blend = 0.5
ldata_spot.use_shadow = False
lobj_spot = bpy.data.objects.new(name="Light_1F_FireplaceSpotDown", object_data=ldata_spot)
lobj_spot.location = (fx, fy, 1.34)
lobj_spot.rotation_euler = (math.radians(180), 0, 0)
col_int.objects.link(lobj_spot)

# Save changes to main blend file
bpy.ops.wm.save_mainfile()
print("MAINFILE_SAVED_WITH_ENHANCED_FIREPLACE")

# Render test preview at frame 380 (close front view) in Sunset lighting to test fireplace visibility!
world = scene.world
sky_node = world.node_tree.nodes.get("Sky Texture") if (world and world.node_tree) else None
sun = bpy.data.objects.get("Sun_SpringMorning")
l_1f = bpy.data.objects.get("Light_1F_LobbyWarmFill")

if sky_node:
    sky_node.sun_elevation = math.radians(4.0)
    sky_node.sun_rotation = math.radians(245.0)
    sky_node.air_density = 2.0
if sun:
    sun.data.energy = 7.5
    sun.data.color = (1.0, 0.45, 0.15)
    sun.rotation_euler = (math.radians(84.0), 0.0, math.radians(245.0))
if l_1f:
    l_1f.data.energy = 380.0

scene.frame_set(380)
out_test = r"E:\ai랩\AI자율회사만들기\scratch\test_fireplace_f380.png"
scene.render.filepath = out_test
bpy.ops.render.render(write_still=True)
print("TEST_STILL_RENDERED:", out_test)

