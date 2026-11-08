"""1. Make 1F modern linear fireplace prominently visible, elevated, and vividly glowing.
2. Render 4 cinematic time-of-day videos (Morning, Noon, Sunset, Night) at 1080p, 24fps."""
import bpy
import math
import os
import subprocess
from mathutils import Vector, Euler

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
OUT_DIR = os.path.join(ROOT, "renders_time_of_day")
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# STEP 1: UPGRADE & ELEVATE THE 1F FIREPLACE TO BE PROMINENTLY VISIBLE
# -------------------------------------------------------------------------
# Reposition fireplace hearth & flames so they sit at eye level above the front terrace lip
sur = bpy.data.objects.get("1F_Lounge_FireplaceSurround")
hearth = bpy.data.objects.get("1F_Lounge_FireplaceHearthBench")
firebox = bpy.data.objects.get("1F_Lounge_FireboxRecess")
flame = bpy.data.objects.get("1F_Lounge_FireFlameGlow")
strip = bpy.data.objects.get("1F_Lounge_FireTopWarmStrip")

# Bring fireplace slightly forward (Y: 0.30 -> -0.10) and raise Z so it is 100% visible through 1F glass!
# Fireplace location: X = 0.85 (clearly between mullions 0.0 and 2.2), Y = -0.15
fx, fy = 0.85, -0.15

if sur:
    sur.location = (fx, fy + 0.14, 1.40)
    sur.scale = (2.40, 0.35, 2.20)
if hearth:
    hearth.location = (fx, fy, 0.55) # Elevated hearth bench
    hearth.scale = (2.60, 0.65, 0.45)
if firebox:
    firebox.location = (fx, fy + 0.04, 1.05) # Centered at Z = 1.05m
    firebox.scale = (1.90, 0.12, 0.55)
if flame:
    flame.location = (fx, fy + 0.03, 0.96)
    flame.scale = (1.75, 0.10, 0.32) # Bigger, taller roaring flame ribbon!
if strip:
    strip.location = (fx, fy + 0.02, 1.32)
    strip.scale = (1.85, 0.06, 0.05)

# Ultra-intense glowing bio-ethanol flame material (Emission Strength 45.0 + deep fiery gradient)
mat_fire = bpy.data.materials.get("Mat_1F_FireplaceFlame")
if mat_fire and mat_fire.node_tree:
    bsdf = mat_fire.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (1.0, 0.42, 0.08, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 45.0
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (1.0, 0.42, 0.08, 1.0)

# Add a dedicated warm dancing Fireplace Point Light inside the firebox!
old_fire_light = bpy.data.objects.get("Light_1F_FireplacePointGlow")
if old_fire_light:
    bpy.data.objects.remove(old_fire_light, do_unlink=True)
col_int = bpy.data.collections.get("04_Interior_Workspace") or bpy.context.scene.collection
ldata_fire = bpy.data.lights.new(name="Light_1F_FireplacePointGlow", type='POINT')
ldata_fire.energy = 380.0
ldata_fire.color = (1.0, 0.45, 0.12)
ldata_fire.shadow_soft_size = 0.35
ldata_fire.use_shadow = False
lobj_fire = bpy.data.objects.new(name="Light_1F_FireplacePointGlow", object_data=ldata_fire)
lobj_fire.location = (fx, fy - 0.05, 1.05)
col_int.objects.link(lobj_fire)

print("FIREPLACE_UPGRADED_SUCCESS")

# -------------------------------------------------------------------------
# STEP 2: CONFIGURE TIME OF DAY LIGHTING PRESETS
# -------------------------------------------------------------------------
scene = bpy.context.scene
world = scene.world
sky_node = world.node_tree.nodes.get("Sky Texture") if (world and world.node_tree) else None
bg_node = world.node_tree.nodes.get("Background") if (world and world.node_tree) else None
sun = bpy.data.objects.get("Sun_SpringMorning")
l_1f = bpy.data.objects.get("Light_1F_LobbyWarmFill")
l_garden = bpy.data.objects.get("Light_CliffGardenWarmGlow")

def set_time_of_day(time_name):
    if time_name == "morning":
        if sky_node:
            sky_node.sun_elevation = math.radians(10.0)
            sky_node.sun_rotation = math.radians(115.0)
            sky_node.altitude = 120.0
            sky_node.air_density = 1.0
        if sun:
            sun.data.energy = 4.8
            sun.data.color = (1.0, 0.94, 0.85)
            sun.rotation_euler = (math.radians(65.0), 0.0, math.radians(115.0))
        if l_1f: l_1f.data.energy = 220.0
        if l_garden: l_garden.data.energy = 280.0
        if lobj_fire: lobj_fire.data.energy = 350.0
        
    elif time_name == "noon":
        if sky_node:
            sky_node.sun_elevation = math.radians(68.0)
            sky_node.sun_rotation = math.radians(180.0)
            sky_node.altitude = 250.0
            sky_node.air_density = 0.70
        if sun:
            sun.data.energy = 6.8
            sun.data.color = (1.0, 0.98, 0.95)
            sun.rotation_euler = (math.radians(22.0), 0.0, math.radians(180.0))
        if l_1f: l_1f.data.energy = 100.0
        if l_garden: l_garden.data.energy = 50.0
        if lobj_fire: lobj_fire.data.energy = 280.0
        
    elif time_name == "sunset":
        if sky_node:
            sky_node.sun_elevation = math.radians(3.8)
            sky_node.sun_rotation = math.radians(245.0)
            sky_node.altitude = 40.0
            sky_node.air_density = 2.2
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 2.5
        if sun:
            sun.data.energy = 8.5
            sun.data.color = (1.0, 0.44, 0.12)
            sun.rotation_euler = (math.radians(84.0), 0.0, math.radians(245.0))
        if l_1f: l_1f.data.energy = 380.0
        if l_garden: l_garden.data.energy = 520.0
        if lobj_fire: lobj_fire.data.energy = 550.0
        
    elif time_name == "night":
        if sky_node:
            sky_node.sun_elevation = math.radians(-12.0)
            sky_node.sun_rotation = math.radians(0.0)
            sky_node.air_density = 1.0
        if bg_node:
            bg_node.inputs['Color'].default_value = (0.012, 0.022, 0.045, 1.0)
            bg_node.inputs['Strength'].default_value = 0.55
        if sun:
            sun.data.energy = 0.45
            sun.data.color = (0.45, 0.65, 1.0)
            sun.rotation_euler = (math.radians(45.0), 0.0, math.radians(40.0))
        if l_1f: l_1f.data.energy = 460.0
        if l_garden: l_garden.data.energy = 650.0
        if lobj_fire: lobj_fire.data.energy = 680.0

# Save updated blend file with new prominent fireplace
bpy.ops.wm.save_mainfile()
print("BLEND_FILE_SAVED_WITH_FIREPLACE")

