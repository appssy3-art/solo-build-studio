import bpy
import math
import os

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
TEST_DIR = os.path.join(ROOT, "scratch", "seasonal_tests_v3")
os.makedirs(TEST_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene
world = scene.world

# Common render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

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

roof_snow = bpy.data.objects.get("Winter_Roof_SnowCaps")

mat_sakura_cloud = bpy.data.materials.get("Mat_SakuraCloud")
mat_sakura_bark = bpy.data.materials.get("Mat_SakuraBark")
mat_skypark_grass = bpy.data.materials.get("Mat_SkyparkGrass")
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

def set_emission(mat, col, strength):
    if not mat or not mat.node_tree: return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*col, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength

def apply_season(season_name):
    is_winter = (season_name == "winter")
    is_autumn = (season_name == "autumn")
    is_summer = (season_name == "summer")
    
    # 1. Snow Cap
    if roof_snow:
        roof_snow.hide_render = not is_winter
        roof_snow.hide_viewport = not is_winter

    # 2. Tree Foliage Alpha (Winter shows bare branches!)
    if mat_sakura_cloud and mat_sakura_cloud.node_tree:
        bsdf = mat_sakura_cloud.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Alpha"].default_value = 0.0 if is_winter else 1.0
        mat_sakura_cloud.blend_method = 'BLEND'

    # 3. Particle System & Flutter Objects
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
                ps.settings.count = 2200
                ps.settings.particle_size = 1.65 # High visibility 5-lobed maple leaf
                ps.settings.size_random = 0.55
                ps.settings.effector_weights.gravity = 0.12
                ps.settings.damping = 0.10
                ps.settings.drag_factor = 0.30
            elif is_winter:
                if obj_sakura:
                    ps.settings.instance_object = obj_sakura
                ps.settings.count = 2600
                ps.settings.particle_size = 0.45 # Soft white snow crystals
                ps.settings.size_random = 0.70
                ps.settings.effector_weights.gravity = 0.22
                ps.settings.damping = 0.08
                ps.settings.drag_factor = 0.15
            else: # Spring
                if obj_sakura:
                    ps.settings.instance_object = obj_sakura
                ps.settings.count = 1800
                ps.settings.particle_size = 0.85
                ps.settings.size_random = 0.45

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

    # 4. Seasonal Specific Lighting & Materials
    if is_summer:
        # Crisp clear summer sky, high sun, saturated turquoise ocean
        if sky_node:
            sky_node.sun_elevation = math.radians(64.0)
            sky_node.sun_rotation = math.radians(160.0)
            sky_node.altitude = 150.0
            sky_node.air_density = 0.50
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 1.5
        if sun:
            sun.data.energy = 8.5
            sun.data.color = (1.0, 0.99, 0.95)
            sun.rotation_euler = (math.radians(26.0), 0.0, math.radians(160.0))
        # Vivid summer greens
        set_color_ramp(mat_sakura_cloud, (0.02, 0.24, 0.05), (0.08, 0.46, 0.12)) # Lush green canopy
        set_color_ramp(mat_skypark_grass, (0.06, 0.36, 0.05), (0.15, 0.52, 0.12))
        set_bsdf_color(mat_cliff_moss, (0.05, 0.24, 0.06))
        set_bsdf_color(mat_cliff_lime, (0.10, 0.36, 0.08))
        set_bsdf_color(mat_azalea, (0.95, 0.18, 0.32)) # Summer blooms
        # Distinct vivid turquoise to sapphire sea!
        set_color_ramp(mat_ocean, (0.01, 0.52, 0.72), (0.005, 0.16, 0.46))
        set_color_ramp(mat_shale, (0.045, 0.048, 0.055), (0.14, 0.15, 0.165))
        set_bsdf_color(mat_teak, (0.24, 0.14, 0.09))
        set_bsdf_color(mat_step, (0.24, 0.14, 0.09))
        set_bsdf_color(mat_trav, (0.32, 0.30, 0.27))
        set_bsdf_color(mat_sakura_bark, (0.15, 0.10, 0.07))
        # Lights
        if l_1f: l_1f.data.energy = 160.0
        if l_garden: l_garden.data.energy = 80.0
        if l_fire: l_fire.data.energy = 500.0
        # Flames
        set_emission(mat_outer, (1.0, 0.25, 0.02), 70.0)
        set_emission(mat_core, (1.0, 0.65, 0.10), 100.0)

    elif is_autumn:
        # Fiery autumn sunset: saturated red/golden maple canopy, fluttering red/amber leaves, cozy fireplace
        if sky_node:
            sky_node.sun_elevation = math.radians(7.5)
            sky_node.sun_rotation = math.radians(238.0)
            sky_node.altitude = 40.0
            sky_node.air_density = 2.0
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 2.4
        if sun:
            sun.data.energy = 9.2
            sun.data.color = (1.0, 0.48, 0.12)
            sun.rotation_euler = (math.radians(82.5), 0.0, math.radians(238.0))
        # Fiery Japanese Maple Foliage
        set_color_ramp(mat_sakura_cloud, (0.88, 0.06, 0.02), (1.0, 0.50, 0.03))
        set_color_ramp(mat_skypark_grass, (0.48, 0.28, 0.06), (0.75, 0.50, 0.12))
        set_bsdf_color(mat_cliff_moss, (0.42, 0.25, 0.08))
        set_bsdf_color(mat_cliff_lime, (0.56, 0.35, 0.10))
        set_bsdf_color(mat_azalea, (0.90, 0.32, 0.06))
        # Sunset-tinted ocean
        set_color_ramp(mat_ocean, (0.015, 0.28, 0.45), (0.01, 0.12, 0.28))
        set_color_ramp(mat_shale, (0.06, 0.05, 0.04), (0.18, 0.14, 0.12))
        set_bsdf_color(mat_teak, (0.22, 0.12, 0.07))
        set_bsdf_color(mat_step, (0.22, 0.12, 0.07))
        set_bsdf_color(mat_trav, (0.30, 0.26, 0.22))
        set_bsdf_color(mat_sakura_bark, (0.16, 0.10, 0.06))
        set_bsdf_color(mat_petal, (0.95, 0.22, 0.02))
        set_bsdf_color(mat_flutter, (0.98, 0.45, 0.04))
        # Autumn warm interior lighting & fireplace
        if l_1f: l_1f.data.energy = 480.0
        if l_garden: l_garden.data.energy = 600.0
        if l_fire: l_fire.data.energy = 1500.0
        if l_spot: l_spot.data.energy = 750.0
        # Intense fiery flames
        set_emission(mat_outer, (1.0, 0.22, 0.01), 110.0)
        set_emission(mat_core, (1.0, 0.62, 0.06), 160.0)
        set_emission(mat_ember, (1.0, 0.14, 0.01), 65.0)

    elif is_winter:
        # Crisp winter: thick snow blankets, bare branches, crystal snowflakes, and BLAZING ROARING FIREPLACE
        if sky_node:
            sky_node.sun_elevation = math.radians(15.0)
            sky_node.sun_rotation = math.radians(145.0)
            sky_node.altitude = 50.0
            sky_node.air_density = 0.65
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 1.2
        if sun:
            sun.data.energy = 4.8
            sun.data.color = (0.86, 0.92, 1.0) # Crisp cold winter light
            sun.rotation_euler = (math.radians(62.0), 0.0, math.radians(145.0))
        # Snowy ground & cliffs
        set_color_ramp(mat_skypark_grass, (0.90, 0.94, 0.98), (0.98, 0.99, 1.0))
        set_bsdf_color(mat_cliff_moss, (0.88, 0.91, 0.96))
        set_bsdf_color(mat_cliff_lime, (0.90, 0.93, 0.97))
        set_bsdf_color(mat_azalea, (0.93, 0.95, 0.98))
        set_color_ramp(mat_shale, (0.55, 0.60, 0.68), (0.92, 0.95, 0.98))
        set_bsdf_color(mat_teak, (0.84, 0.87, 0.92))
        set_bsdf_color(mat_step, (0.84, 0.87, 0.92))
        set_bsdf_color(mat_trav, (0.90, 0.93, 0.96))
        # Cold deep northern ocean with white wave crests
        set_color_ramp(mat_ocean, (0.01, 0.24, 0.40), (0.005, 0.08, 0.20))
        set_bsdf_color(mat_petal, (0.98, 0.99, 1.0)) # Snowflakes
        set_bsdf_color(mat_flutter, (0.97, 0.98, 1.0))
        set_bsdf_color(mat_sakura_bark, (0.10, 0.08, 0.07))
        # Winter interior lighting: fireplace is the warm beating heart of the house!
        if l_1f: l_1f.data.energy = 550.0
        if l_garden: l_garden.data.energy = 700.0
        if l_fire:
            l_fire.data.energy = 2200.0 # ROARING warm fire glow!
            l_fire.data.color = (1.0, 0.36, 0.03)
        if l_spot: l_spot.data.energy = 900.0
        # Blazing hot flame materials
        set_emission(mat_outer, (1.0, 0.18, 0.005), 130.0)
        set_emission(mat_core, (1.0, 0.60, 0.04), 180.0)
        set_emission(mat_ember, (1.0, 0.12, 0.005), 80.0)

# Render frame 220 for Summer, Autumn, Winter
scene.frame_set(220)
for s_id in ["summer", "autumn", "winter"]:
    print(f"Applying {s_id} for frame 220 preview...")
    apply_season(s_id)
    out_path = os.path.join(TEST_DIR, f"preview_{s_id}_f220.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {out_path}")

