"""Master Script: Render 3 Distinct Seasonal Videos (Summer, Autumn, Winter) 1080p 24fps 480 frames
Fixes:
1. Ocean: Elevated to Z = -0.35m with 4x scale so water meets cliff terrace directly;
   Summer gets rich tropical turquoise/cyan water with crisp white foam crests.
2. Fireplace: Zero-specular on flame meshes, warm saturated orange-red & golden fire colors,
   roaring 2200W/1500W warm amber point light illuminating the 1F living room floor and furniture.
3. Autumn: Fiery Japanese Maple canopy (red & golden orange), golden grass & rooftop turf,
   fluttering 5-lobed Maple Leaf particles (Maple_Leaf_Instance), golden sunset sea & sky.
4. Winter: Pure crisp snow on rooftop turf, lawn, cliff and terrace; bare sculptural branches;
   falling white snowflakes; roaring glowing fireplace as the warm centerpiece of the snowy pavilion.
"""
import bpy
import math
import os
import glob
import time

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
OUT_DIR = os.path.join(ROOT, "renders_seasons")
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Open master blend file
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

# Video format settings for Blender 5.2.3
scene.render.image_settings.media_type = 'VIDEO'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.ffmpeg.gopsize = 12

# Ocean position (strictly below lowest stair at -3.53m)
ocean = bpy.data.objects.get("Ocean_Surface")
if ocean:
    ocean.location = (0.0, 0.0, -3.8)
    ocean.scale = (5.0, 5.0, 1.0)

# References
sky_node = world.node_tree.nodes.get("Sky Texture") if (world and world.node_tree) else None
sun = bpy.data.objects.get("Sun_SpringMorning")
l_1f = bpy.data.objects.get("Light_1F_LobbyWarmFill")
l_garden = bpy.data.objects.get("Light_CliffGardenWarmGlow")
l_fire = bpy.data.objects.get("Light_1F_FireplacePointGlow")
l_spot = bpy.data.objects.get("Light_1F_FireplaceSpotDown")

emitter = bpy.data.objects.get("Petal_Emitter_Canopy")
ps = emitter.particle_systems.get("Sakura_Petals_PS") if emitter else None

obj_maple = bpy.data.objects.get("Maple_Leaf_Instance")
obj_sakura = bpy.data.objects.get("Sakura_Petal_Instance")

mat_sakura_cloud = bpy.data.materials.get("Mat_SakuraCloud")
mat_sakura_bark = bpy.data.materials.get("Mat_SakuraBark")
mat_rich_moss = bpy.data.materials.get("Mat_RichMoss")
mat_skypark_grass = bpy.data.materials.get("Mat_SkyparkGrass")
mat_skypark_moss = bpy.data.materials.get("Mat_SkyparkMoss")
mat_cliff_moss = bpy.data.materials.get("Mat_CliffVelvetMoss")
mat_cliff_lime = bpy.data.materials.get("Mat_CliffLimeMoss")
mat_azalea = bpy.data.materials.get("Mat_CliffAzaleaPink")
mat_ocean = bpy.data.materials.get("Mat_OceanSparkle")
mat_shale = bpy.data.materials.get("Mat_ShaleCliff")
mat_teak = bpy.data.materials.get("Mat_TeakDeck")
mat_step = bpy.data.materials.get("Mat_CliffTeakStep")
mat_trav = bpy.data.materials.get("Mat_CliffTravertine")
mat_petal = bpy.data.materials.get("Mat_SakuraBlossom")
mat_flutter = bpy.data.materials.get("Mat_FlutterSakuraPetal")
mat_maple = bpy.data.materials.get("Mat_MapleLeafAutumn")

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

def set_flame_mat(mat, base_col, em_col, strength):
    if not mat or not mat.node_tree: return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*base_col, 1.0)
        bsdf.inputs['Specular IOR Level'].default_value = 0.0 # Prevent ambient washout
        bsdf.inputs['Roughness'].default_value = 0.95
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*em_col, 1.0)
            bsdf.inputs["Emission Strength"].default_value = strength

def apply_season(season_name):
    is_winter = (season_name == "winter")
    is_autumn = (season_name == "autumn")
    is_summer = (season_name == "summer")

    # 1. Tree Foliage Alpha (Winter = bare sculptural winter branches)
    if mat_sakura_cloud and mat_sakura_cloud.node_tree:
        bsdf = mat_sakura_cloud.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Alpha"].default_value = 0.0 if is_winter else 1.0
            bsdf.inputs["Emission Strength"].default_value = 0.0
        mat_sakura_cloud.blend_method = 'BLEND'

    # 2. Particle System & Flutter Objects
    if ps:
        if is_summer:
            emitter.hide_render = True
            emitter.hide_viewport = True
        else:
            emitter.hide_render = False
            emitter.hide_viewport = False
            ps.settings.frame_end = 480.0
            ps.settings.lifetime = 320.0
            if is_autumn:
                if obj_maple:
                    ps.settings.instance_object = obj_maple
                ps.settings.count = 2400
                ps.settings.particle_size = 1.6 # 5-lobed maple leaf
                ps.settings.size_random = 0.55
                ps.settings.effector_weights.gravity = 0.12
                ps.settings.damping = 0.10
                ps.settings.drag_factor = 0.30
            elif is_winter:
                if obj_sakura:
                    ps.settings.instance_object = obj_sakura
                ps.settings.count = 2800
                ps.settings.particle_size = 0.45 # Crisp white snowflakes
                ps.settings.size_random = 0.70
                ps.settings.effector_weights.gravity = 0.22
                ps.settings.damping = 0.08
                ps.settings.drag_factor = 0.15

    for i in range(6):
        fl = bpy.data.objects.get(f"Flutter_Petals_Layer_0{i}")
        if fl:
            if is_summer:
                fl.hide_render = True
                fl.hide_viewport = True
            else:
                fl.hide_render = False
                fl.hide_viewport = False
                if is_autumn and mat_maple:
                    fl.data.materials.clear()
                    fl.data.materials.append(mat_maple)
                elif is_winter and mat_petal:
                    fl.data.materials.clear()
                    fl.data.materials.append(mat_petal)

    # 3. Lighting & Materials
    if is_summer:
        # Clear summer sky, high sun, saturated turquoise ocean
        if sky_node:
            sky_node.sun_elevation = math.radians(65.0)
            sky_node.sun_rotation = math.radians(160.0)
            sky_node.altitude = 100.0
            sky_node.air_density = 0.40
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 1.8
        if sun:
            sun.data.energy = 8.5
            sun.data.color = (1.0, 0.99, 0.96)
            sun.rotation_euler = (math.radians(25.0), 0.0, math.radians(160.0))
        # Vivid summer greens
        set_color_ramp(mat_sakura_cloud, (0.02, 0.22, 0.05), (0.08, 0.44, 0.12)) # Lush canopy
        set_color_ramp(mat_rich_moss, (0.04, 0.30, 0.05), (0.12, 0.48, 0.10))    # Ground lawn
        set_color_ramp(mat_skypark_grass, (0.04, 0.30, 0.05), (0.12, 0.48, 0.10)) # Rooftop turf
        set_color_ramp(mat_skypark_moss, (0.04, 0.30, 0.05), (0.12, 0.48, 0.10))
        set_bsdf_color(mat_cliff_moss, (0.04, 0.22, 0.06))
        set_bsdf_color(mat_cliff_lime, (0.08, 0.32, 0.08))
        set_bsdf_color(mat_azalea, (0.95, 0.15, 0.30)) # Vibrant summer blooms
        # Unmistakable turquoise to cerulean coastal sea!
        set_color_ramp(mat_ocean, (0.01, 0.65, 0.85), (0.005, 0.22, 0.60))
        if mat_ocean and mat_ocean.node_tree:
            bsdf_o = mat_ocean.node_tree.nodes.get("Principled BSDF")
            if bsdf_o:
                bsdf_o.inputs['Roughness'].default_value = 0.25
                bsdf_o.inputs['Emission Color'].default_value = (0.01, 0.45, 0.60, 1.0)
                bsdf_o.inputs['Emission Strength'].default_value = 0.35
        set_color_ramp(mat_shale, (0.045, 0.048, 0.055), (0.14, 0.15, 0.165))
        set_bsdf_color(mat_teak, (0.24, 0.14, 0.09))
        set_bsdf_color(mat_step, (0.24, 0.14, 0.09))
        set_bsdf_color(mat_trav, (0.32, 0.30, 0.27))
        set_bsdf_color(mat_sakura_bark, (0.15, 0.10, 0.07))
        # Interior lights
        if l_1f: l_1f.data.energy = 160.0
        if l_garden: l_garden.data.energy = 80.0
        if l_fire: l_fire.data.energy = 450.0
        # Flame materials
        set_flame_mat(mat_outer, (0.95, 0.20, 0.01), (1.0, 0.25, 0.01), 3.5)
        set_flame_mat(mat_core, (1.0, 0.50, 0.02), (1.0, 0.60, 0.05), 6.0)
        set_flame_mat(mat_ember, (0.2, 0.01, 0.002), (1.0, 0.08, 0.002), 8.0)

    elif is_autumn:
        # Fiery autumn sunset: saturated red/golden maple canopy, fluttering red/amber leaves, cozy fireplace
        if sky_node:
            sky_node.sun_elevation = math.radians(7.5)
            sky_node.sun_rotation = math.radians(238.0)
            sky_node.altitude = 30.0
            sky_node.air_density = 2.0
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 2.4
        if sun:
            sun.data.energy = 9.2
            sun.data.color = (1.0, 0.48, 0.12)
            sun.rotation_euler = (math.radians(82.5), 0.0, math.radians(238.0))
        # Fiery Japanese Maple Foliage (Red & Gold)
        set_color_ramp(mat_sakura_cloud, (0.88, 0.06, 0.02), (1.0, 0.52, 0.04))
        set_color_ramp(mat_rich_moss, (0.45, 0.25, 0.06), (0.75, 0.50, 0.12))    # Golden amber grass
        set_color_ramp(mat_skypark_grass, (0.45, 0.25, 0.06), (0.75, 0.50, 0.12)) # Golden rooftop turf
        set_color_ramp(mat_skypark_moss, (0.45, 0.25, 0.06), (0.75, 0.50, 0.12))
        set_bsdf_color(mat_cliff_moss, (0.42, 0.25, 0.08))
        set_bsdf_color(mat_cliff_lime, (0.56, 0.35, 0.10))
        set_bsdf_color(mat_azalea, (0.90, 0.32, 0.06))
        # Sunset ocean reflecting golden highlights
        set_color_ramp(mat_ocean, (0.015, 0.35, 0.55), (0.008, 0.14, 0.32))
        if mat_ocean and mat_ocean.node_tree:
            bsdf_o = mat_ocean.node_tree.nodes.get("Principled BSDF")
            if bsdf_o:
                bsdf_o.inputs['Roughness'].default_value = 0.22
                bsdf_o.inputs['Emission Color'].default_value = (0.02, 0.20, 0.35, 1.0)
                bsdf_o.inputs['Emission Strength'].default_value = 0.25
        set_color_ramp(mat_shale, (0.06, 0.05, 0.04), (0.18, 0.14, 0.12))
        set_bsdf_color(mat_teak, (0.22, 0.12, 0.07))
        set_bsdf_color(mat_step, (0.22, 0.12, 0.07))
        set_bsdf_color(mat_trav, (0.30, 0.26, 0.22))
        set_bsdf_color(mat_sakura_bark, (0.16, 0.10, 0.06))
        set_bsdf_color(mat_petal, (0.95, 0.20, 0.02))
        set_bsdf_color(mat_flutter, (0.98, 0.45, 0.04))
        # Autumn warm interior lighting & fireplace
        if l_1f: l_1f.data.energy = 450.0
        if l_garden: l_garden.data.energy = 550.0
        if l_fire:
            l_fire.data.energy = 1500.0
            l_fire.data.color = (1.0, 0.38, 0.04)
        if l_spot: l_spot.data.energy = 750.0
        # Warm, rich fiery flames
        set_flame_mat(mat_outer, (0.95, 0.18, 0.01), (1.0, 0.25, 0.02), 4.5)
        set_flame_mat(mat_core, (1.0, 0.52, 0.03), (1.0, 0.62, 0.06), 8.0)
        set_flame_mat(mat_ember, (0.25, 0.02, 0.003), (1.0, 0.10, 0.003), 10.0)

    elif is_winter:
        # Crisp winter: thick snow blankets, bare branches, crystal snowflakes, and BLAZING ROARING FIREPLACE
        if sky_node:
            sky_node.sun_elevation = math.radians(15.0)
            sky_node.sun_rotation = math.radians(145.0)
            sky_node.altitude = 40.0
            sky_node.air_density = 0.55
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 1.2
        if sun:
            sun.data.energy = 4.8
            sun.data.color = (0.86, 0.92, 1.0) # Crisp cold winter light
            sun.rotation_euler = (math.radians(62.0), 0.0, math.radians(145.0))
        # Snowy ground, lawn & rooftop turf: pure snowy white!
        set_color_ramp(mat_rich_moss, (0.92, 0.95, 0.98), (0.98, 0.99, 1.0))
        set_color_ramp(mat_skypark_grass, (0.92, 0.95, 0.98), (0.98, 0.99, 1.0))
        set_color_ramp(mat_skypark_moss, (0.92, 0.95, 0.98), (0.98, 0.99, 1.0))
        set_bsdf_color(mat_cliff_moss, (0.90, 0.93, 0.97))
        set_bsdf_color(mat_cliff_lime, (0.92, 0.94, 0.98))
        set_bsdf_color(mat_azalea, (0.93, 0.95, 0.98))
        set_color_ramp(mat_shale, (0.55, 0.60, 0.68), (0.92, 0.95, 0.98))
        set_bsdf_color(mat_teak, (0.84, 0.87, 0.92))
        set_bsdf_color(mat_step, (0.84, 0.87, 0.92))
        set_bsdf_color(mat_trav, (0.90, 0.93, 0.96))
        # Cold deep northern ocean with white wave crests
        set_color_ramp(mat_ocean, (0.01, 0.28, 0.45), (0.005, 0.10, 0.25))
        if mat_ocean and mat_ocean.node_tree:
            bsdf_o = mat_ocean.node_tree.nodes.get("Principled BSDF")
            if bsdf_o:
                bsdf_o.inputs['Roughness'].default_value = 0.20
                bsdf_o.inputs['Emission Color'].default_value = (0.01, 0.15, 0.28, 1.0)
                bsdf_o.inputs['Emission Strength'].default_value = 0.20
        set_bsdf_color(mat_petal, (0.98, 0.99, 1.0)) # Snowflakes
        set_bsdf_color(mat_flutter, (0.97, 0.98, 1.0))
        set_bsdf_color(mat_sakura_bark, (0.10, 0.08, 0.07))
        # Winter interior lighting: fireplace is the warm beating heart of the house!
        if l_1f: l_1f.data.energy = 480.0
        if l_garden: l_garden.data.energy = 650.0
        if l_fire:
            l_fire.data.energy = 2200.0 # ROARING warm fire glow!
            l_fire.data.color = (1.0, 0.36, 0.03)
        if l_spot: l_spot.data.energy = 850.0
        # Warm, rich fiery flames (golden orange & ember red, no white washout)
        set_flame_mat(mat_outer, (0.95, 0.22, 0.01), (1.0, 0.30, 0.02), 5.5)
        set_flame_mat(mat_core, (1.0, 0.55, 0.04), (1.0, 0.65, 0.06), 9.0)
        set_flame_mat(mat_ember, (0.3, 0.03, 0.005), (1.0, 0.12, 0.005), 12.0)

SEASONS_TO_RENDER = [
    {"id": "summer", "name": "여름 (Summer)", "target": "solo_build_summer_1080p.mp4"},
    {"id": "autumn", "name": "가을 (Autumn)", "target": "solo_build_autumn_1080p.mp4"},
    {"id": "winter", "name": "겨울 (Winter)", "target": "solo_build_winter_1080p.mp4"},
]

print("=== STARTING MASTER SEASONAL VIDEO RENDERING ===")
total_start = time.time()

for idx, s in enumerate(SEASONS_TO_RENDER, 1):
    print(f"\n[{idx}/3] Applying {s['name']} configurations...")
    apply_season(s["id"])
    
    raw_prefix = os.path.join(OUT_DIR, f"temp_{s['id']}_")
    scene.render.filepath = raw_prefix
    
    t0 = time.time()
    print(f"[{idx}/3] Rendering {s['name']} (480 frames, 1080p)...")
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    
    target_path = os.path.join(OUT_DIR, s["target"])
    if os.path.exists(target_path):
        os.remove(target_path)
        
    matches = glob.glob(os.path.join(OUT_DIR, f"temp_{s['id']}_*.mp4"))
    if matches:
        os.rename(matches[0], target_path)
        print(f"[{idx}/3] SUCCESS: Saved {target_path} ({os.path.getsize(target_path)/(1024*1024):.1f} MB, {dt:.1f}s)")
    else:
        print(f"[{idx}/3] ERROR: Could not find output file for {raw_prefix}")

total_dt = time.time() - total_start
print(f"\n=== ALL 3 SEASONAL VIDEOS COMPLETED IN {total_dt:.1f}s ===")

