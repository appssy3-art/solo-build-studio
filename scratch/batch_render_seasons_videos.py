"""Batch render 3 cinematic seasonal videos (Summer, Autumn, Winter)
at 1920x1080 24fps (480 frames, 20s each) using Blender EEVEE."""
import bpy
import math
import os
import glob
import time
import shutil

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
OUT_DIR = os.path.join(ROOT, "renders_seasons")
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Open blend file
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
mat_sakura_cloud = bpy.data.materials.get("Mat_SakuraCloud")
mat_skypark_grass = bpy.data.materials.get("Mat_SkyparkGrass")
mat_cliff_moss = bpy.data.materials.get("Mat_CliffVelvetMoss")
mat_cliff_lime = bpy.data.materials.get("Mat_CliffLimeMoss")
mat_azalea = bpy.data.materials.get("Mat_CliffAzaleaPink")
mat_ocean = bpy.data.materials.get("Mat_OceanSparkle")

mat_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
mat_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")

def set_color_ramp(mat, stop0_col, stop1_col):
    if not mat or not mat.node_tree: return
    cramp = mat.node_tree.nodes.get("Color Ramp")
    if cramp:
        cramp.color_ramp.elements[0].color = (*stop0_col, 1.0)
        cramp.color_ramp.elements[1].color = (*stop1_col, 1.0)
    else:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf and not bsdf.inputs["Base Color"].is_linked:
            bsdf.inputs["Base Color"].default_value = (*stop0_col, 1.0)

def set_bsdf_color(mat, col):
    if not mat or not mat.node_tree: return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*col, 1.0)

SEASONS = [
    {
        "id": "summer",
        "name": "여름 (Summer)",
        "target_name": "solo_build_summer_1080p.mp4",
        # Lighting: Bright vibrant midday summer sun
        "sun_elev": 65.0, "sun_rot": 160.0, "altitude": 220.0, "air_density": 0.65,
        "sun_energy": 7.5, "sun_color": (1.0, 0.99, 0.96), "sun_rx": 25.0, "sun_rz": 160.0,
        "l_1f": 140.0, "l_garden": 80.0, "l_fire": 450.0, "l_spot": 220.0,
        "flame_mult": 0.85,
        # Materials: Deep emerald foliage & turquoise ocean
        "trees": ((0.04, 0.22, 0.06), (0.12, 0.42, 0.15)),
        "grass": ((0.08, 0.38, 0.06), (0.18, 0.52, 0.14)),
        "moss": (0.07, 0.25, 0.08),
        "lime": (0.12, 0.38, 0.10),
        "flower": (0.98, 0.22, 0.35),
        "ocean": ((0.005, 0.15, 0.22), (0.02, 0.32, 0.45))
    },
    {
        "id": "autumn",
        "name": "가을 (Autumn)",
        "target_name": "solo_build_autumn_1080p.mp4",
        # Lighting: Rich golden sunset / twilight hour
        "sun_elev": 6.0, "sun_rot": 235.0, "altitude": 45.0, "air_density": 2.1,
        "sun_energy": 8.2, "sun_color": (1.0, 0.48, 0.12), "sun_rx": 82.0, "sun_rz": 235.0,
        "l_1f": 420.0, "l_garden": 520.0, "l_fire": 1050.0, "l_spot": 550.0,
        "flame_mult": 1.35,
        # Materials: Crimson maple red & golden-orange amber
        "trees": ((0.75, 0.12, 0.03), (0.98, 0.42, 0.06)),
        "grass": ((0.48, 0.30, 0.10), (0.72, 0.48, 0.16)),
        "moss": (0.42, 0.28, 0.10),
        "lime": (0.55, 0.38, 0.12),
        "flower": (0.88, 0.38, 0.10),
        "ocean": ((0.02, 0.08, 0.15), (0.05, 0.20, 0.28))
    },
    {
        "id": "winter",
        "name": "겨울 (Winter)",
        "target_name": "solo_build_winter_1080p.mp4",
        # Lighting: Frosty cool winter sky with radiant warm interior haven & roaring fire
        "sun_elev": 15.0, "sun_rot": 145.0, "altitude": 60.0, "air_density": 0.70,
        "sun_energy": 4.2, "sun_color": (0.90, 0.94, 1.0), "sun_rx": 58.0, "sun_rz": 145.0,
        "l_1f": 560.0, "l_garden": 650.0, "l_fire": 1250.0, "l_spot": 650.0,
        "flame_mult": 1.55,
        # Materials: Pure white snow frosting with cool soft shadows
        "trees": ((0.88, 0.92, 0.96), (0.98, 0.99, 1.0)),
        "grass": ((0.86, 0.90, 0.95), (0.97, 0.98, 1.0)),
        "moss": (0.85, 0.88, 0.92),
        "lime": (0.88, 0.91, 0.95),
        "flower": (0.90, 0.92, 0.96),
        "ocean": ((0.008, 0.03, 0.07), (0.02, 0.06, 0.12))
    }
]

print("=== STARTING BATCH RENDER: 3 SEASONS VIDEOS (SUMMER, AUTUMN, WINTER) ===")
total_start = time.time()

for idx, s in enumerate(SEASONS, 1):
    print(f"\n[{idx}/3] Applying {s['name']} materials & lighting...")
    
    # 1. Apply Materials
    set_color_ramp(mat_sakura_cloud, s["trees"][0], s["trees"][1])
    set_color_ramp(mat_skypark_grass, s["grass"][0], s["grass"][1])
    set_bsdf_color(mat_cliff_moss, s["moss"])
    set_bsdf_color(mat_cliff_lime, s["lime"])
    set_bsdf_color(mat_azalea, s["flower"])
    set_color_ramp(mat_ocean, s["ocean"][0], s["ocean"][1])
    
    # 2. Apply Sky & Lighting
    if sky_node:
        sky_node.sun_elevation = math.radians(s["sun_elev"])
        sky_node.sun_rotation = math.radians(s["sun_rot"])
        sky_node.altitude = s["altitude"]
        sky_node.air_density = s["air_density"]
        if hasattr(sky_node, 'ozone_density'):
            sky_node.ozone_density = 2.5 if s["id"] == "autumn" else 1.0
            
    if bg_node:
        bg_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0
        
    if sun:
        sun.data.energy = s["sun_energy"]
        sun.data.color = s["sun_color"]
        sun.rotation_euler = (math.radians(s["sun_rx"]), 0.0, math.radians(s["sun_rz"]))
        
    if l_1f: l_1f.data.energy = s["l_1f"]
    if l_garden: l_garden.data.energy = s["l_garden"]
    if l_fire: l_fire.data.energy = s["l_fire"]
    if l_spot: l_spot.data.energy = s["l_spot"]
    
    # 3. Fireplace Flame Intensity
    mult = s["flame_mult"]
    if mat_core and mat_core.node_tree:
        bsdf = mat_core.node_tree.nodes.get("Principled BSDF")
        if bsdf: bsdf.inputs["Emission Strength"].default_value = 45.0 * mult
    if mat_outer and mat_outer.node_tree:
        bsdf = mat_outer.node_tree.nodes.get("Principled BSDF")
        if bsdf: bsdf.inputs["Emission Strength"].default_value = 32.0 * mult
    if mat_ember and mat_ember.node_tree:
        bsdf = mat_ember.node_tree.nodes.get("Principled BSDF")
        if bsdf: bsdf.inputs["Emission Strength"].default_value = 35.0 * mult

    # Output path
    raw_prefix = os.path.join(OUT_DIR, f"temp_{s['id']}_")
    scene.render.filepath = raw_prefix
    
    # Render animation!
    t0 = time.time()
    print(f"[{idx}/3] Rendering {s['name']} (480 frames, 1080p)...")
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    
    # Locate generated video file and rename to clean final name
    target_path = os.path.join(OUT_DIR, s["target_name"])
    if os.path.exists(target_path):
        os.remove(target_path)
        
    matches = glob.glob(os.path.join(OUT_DIR, f"temp_{s['id']}_*.mp4"))
    if matches:
        os.rename(matches[0], target_path)
        print(f"[{idx}/3] Saved: {target_path} ({os.path.getsize(target_path)/(1024*1024):.1f} MB, {dt:.1f}s)")
    else:
        print(f"[{idx}/3] WARNING: Could not find generated file for prefix {raw_prefix}")

# Also copy Spring video from renders_time_of_day if available
morning_src = os.path.join(ROOT, "renders_time_of_day", "solo_build_morning_1080p.mp4")
spring_dst = os.path.join(OUT_DIR, "solo_build_spring_1080p.mp4")
if os.path.exists(morning_src) and not os.path.exists(spring_dst):
    shutil.copy2(morning_src, spring_dst)
    print(f"Copied Spring master video to {spring_dst}")

total_dt = time.time() - total_start
print(f"\n=== ALL 3 SEASON VIDEOS RENDERED SUCCESSFULLY in {total_dt:.1f}s! ===")

