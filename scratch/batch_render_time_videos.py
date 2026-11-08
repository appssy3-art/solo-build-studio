"""Batch render 4 cinematic time-of-day videos (Morning, Noon, Sunset, Night)
at 1920x1080 24fps (480 frames, 20s each) using Blender EEVEE."""
import bpy
import math
import os
import glob
import time

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
OUT_DIR = os.path.join(ROOT, "renders_time_of_day")
os.makedirs(OUT_DIR, exist_ok=True)

# Open blend file
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene
world = scene.world

# Common render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 0
scene.frame_end = 480 # 20 seconds drone flight

# Critical for Blender 5+: Set media_type to VIDEO before setting FFMPEG
scene.render.image_settings.media_type = 'VIDEO'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.ffmpeg.gopsize = 12

# Nodes & Objects references
sky_node = world.node_tree.nodes.get("Sky Texture") if (world and world.node_tree) else None
bg_node = world.node_tree.nodes.get("Background") if (world and world.node_tree) else None
sun = bpy.data.objects.get("Sun_SpringMorning")
l_1f = bpy.data.objects.get("Light_1F_LobbyWarmFill")
l_garden = bpy.data.objects.get("Light_CliffGardenWarmGlow")
l_fire = bpy.data.objects.get("Light_1F_FireplacePointGlow")
l_spot = bpy.data.objects.get("Light_1F_FireplaceSpotDown")

# Materials
mat_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
mat_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")

PRESETS = [
    {
        "id": "morning",
        "name": "아침 (Morning)",
        "target_name": "solo_build_morning_1080p.mp4",
        "sun_elev": 12.0, "sun_rot": 110.0, "altitude": 100.0, "air_density": 1.05,
        "sun_energy": 5.5, "sun_color": (1.0, 0.92, 0.82), "sun_rx": 68.0, "sun_rz": 110.0,
        "l_1f": 240.0, "l_garden": 260.0, "l_fire": 650.0, "l_spot": 320.0,
        "flame_mult": 1.0,
        "is_night": False
    },
    {
        "id": "noon",
        "name": "점심 (Noon)",
        "target_name": "solo_build_noon_1080p.mp4",
        "sun_elev": 68.0, "sun_rot": 180.0, "altitude": 250.0, "air_density": 0.65,
        "sun_energy": 7.5, "sun_color": (1.0, 0.98, 0.95), "sun_rx": 22.0, "sun_rz": 180.0,
        "l_1f": 120.0, "l_garden": 80.0, "l_fire": 500.0, "l_spot": 250.0,
        "flame_mult": 0.9,
        "is_night": False
    },
    {
        "id": "sunset",
        "name": "저녁 (Sunset)",
        "target_name": "solo_build_sunset_1080p.mp4",
        "sun_elev": 3.5, "sun_rot": 245.0, "altitude": 40.0, "air_density": 2.3,
        "sun_energy": 8.8, "sun_color": (1.0, 0.42, 0.10), "sun_rx": 84.0, "sun_rz": 245.0,
        "l_1f": 450.0, "l_garden": 550.0, "l_fire": 1100.0, "l_spot": 600.0,
        "flame_mult": 1.4,
        "is_night": False
    },
    {
        "id": "night",
        "name": "밤 (Night)",
        "target_name": "solo_build_night_1080p.mp4",
        "sun_elev": -15.0, "sun_rot": 0.0, "altitude": 50.0, "air_density": 1.0,
        "sun_energy": 0.45, "sun_color": (0.45, 0.65, 1.0), "sun_rx": 45.0, "sun_rz": 40.0,
        "l_1f": 520.0, "l_garden": 750.0, "l_fire": 1300.0, "l_spot": 700.0,
        "flame_mult": 1.6,
        "is_night": True
    }
]

print("=== STARTING BATCH RENDER: 4 TIME OF DAY VIDEOS ===")
total_start = time.time()

for idx, p in enumerate(PRESETS, 1):
    print(f"\n[{idx}/4] Configuring {p['name']}...")
    
    # Sky configuration
    if sky_node:
        sky_node.sun_elevation = math.radians(p["sun_elev"])
        sky_node.sun_rotation = math.radians(p["sun_rot"])
        sky_node.altitude = p["altitude"]
        sky_node.air_density = p["air_density"]
        if hasattr(sky_node, 'ozone_density'):
            sky_node.ozone_density = 2.5 if p["id"] == "sunset" else 1.0
            
    if bg_node:
        if p["is_night"]:
            bg_node.inputs['Color'].default_value = (0.012, 0.022, 0.048, 1.0)
            bg_node.inputs['Strength'].default_value = 0.55
        else:
            bg_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            bg_node.inputs['Strength'].default_value = 1.0
            
    # Sun light configuration
    if sun:
        sun.data.energy = p["sun_energy"]
        sun.data.color = p["sun_color"]
        sun.rotation_euler = (math.radians(p["sun_rx"]), 0.0, math.radians(p["sun_rz"]))
        
    # Interior & Landscape illumination
    if l_1f: l_1f.data.energy = p["l_1f"]
    if l_garden: l_garden.data.energy = p["l_garden"]
    if l_fire: l_fire.data.energy = p["l_fire"]
    if l_spot: l_spot.data.energy = p["l_spot"]
    
    # Flame intensity boost
    mult = p["flame_mult"]
    if mat_core and mat_core.node_tree:
        bsdf = mat_core.node_tree.nodes.get("Principled BSDF")
        if bsdf: bsdf.inputs["Emission Strength"].default_value = 45.0 * mult
    if mat_outer and mat_outer.node_tree:
        bsdf = mat_outer.node_tree.nodes.get("Principled BSDF")
        if bsdf: bsdf.inputs["Emission Strength"].default_value = 32.0 * mult
    if mat_ember and mat_ember.node_tree:
        bsdf = mat_ember.node_tree.nodes.get("Principled BSDF")
        if bsdf: bsdf.inputs["Emission Strength"].default_value = 35.0 * mult

    # Base filepath for blender output
    raw_prefix = os.path.join(OUT_DIR, f"temp_{p['id']}_")
    scene.render.filepath = raw_prefix
    
    # Render animation!
    t0 = time.time()
    print(f"[{idx}/4] Rendering {p['name']} (480 frames, 1080p)...")
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    
    # Locate generated video file and rename to clean final name
    target_path = os.path.join(OUT_DIR, p["target_name"])
    if os.path.exists(target_path):
        os.remove(target_path)
        
    matches = glob.glob(os.path.join(OUT_DIR, f"temp_{p['id']}_*.mp4"))
    if matches:
        os.rename(matches[0], target_path)
        print(f"[{idx}/4] Saved: {target_path} ({os.path.getsize(target_path)/(1024*1024):.1f} MB, {dt:.1f}s)")
    else:
        print(f"[{idx}/4] WARNING: Could not find generated file for prefix {raw_prefix}")

total_dt = time.time() - total_start
print(f"\n=== ALL 4 TIME OF DAY VIDEOS RENDERED SUCCESSFULLY in {total_dt:.1f}s! ===")
