"""Render 4 distinct seasonal test frames (Spring, Summer, Autumn, Winter) at frame 150 & frame 220
with genuine seasonal physical characteristics:
- Spring: Fluttering pink cherry blossom petals, fresh cherry blossom canopy
- Summer: Lush green dense oak canopy, crystal turquoise ocean, NO floating petals (clear summer sky)
- Autumn: Red & golden maple leaf foliage, spinning autumn leaves fluttering in wind, golden hour sunset
- Winter: Thick snow on roof, snow on terrace & lawn, bare winter branches, softly falling white snowflakes
"""
import bpy
import math
import os

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
TEST_DIR = os.path.join(ROOT, "scratch", "seasonal_tests")
os.makedirs(TEST_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene
world = scene.world

# Common nodes & references
sky_node = world.node_tree.nodes.get("Sky Texture") if (world and world.node_tree) else None
bg_node = world.node_tree.nodes.get("Background") if (world and world.node_tree) else None
sun = bpy.data.objects.get("Sun_SpringMorning")
emitter = bpy.data.objects.get("Petal_Emitter_Canopy")
ps = emitter.particle_systems.get("Sakura_Petals_PS") if emitter else None

# Material references
mat_sakura_cloud = bpy.data.materials.get("Mat_SakuraCloud")
mat_sakura_bark = bpy.data.materials.get("Mat_SakuraBark")
mat_skypark_grass = bpy.data.materials.get("Mat_SkyparkGrass")
mat_cliff_moss = bpy.data.materials.get("Mat_CliffVelvetMoss")
mat_cliff_lime = bpy.data.materials.get("Mat_CliffLimeMoss")
mat_azalea = bpy.data.materials.get("Mat_CliffAzaleaPink")
mat_ocean = bpy.data.materials.get("Mat_OceanSparkle")

mat_petal = bpy.data.materials.get("Mat_SakuraBlossom")
mat_flutter = bpy.data.materials.get("Mat_FlutterSakuraPetal")

mat_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
mat_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")

l_1f = bpy.data.objects.get("Light_1F_LobbyWarmFill")
l_garden = bpy.data.objects.get("Light_CliffGardenWarmGlow")
l_fire = bpy.data.objects.get("Light_1F_FireplacePointGlow")
l_spot = bpy.data.objects.get("Light_1F_FireplaceSpotDown")

# 1. Create Snow Cap Objects for Winter if not existing
roof = bpy.data.objects.get("Studio_AeroRoofShell")
roof_snow = bpy.data.objects.get("Winter_Roof_SnowCaps")
if not roof_snow and roof:
    roof_snow = roof.copy()
    roof_snow.data = roof.data.copy()
    roof_snow.name = "Winter_Roof_SnowCaps"
    scene.collection.objects.link(roof_snow)
    roof_snow.location.z = 0.04
    mod = roof_snow.modifiers.new(name="SnowSolidify", type='SOLIDIFY')
    mod.thickness = 0.14
    mod.offset = 1.0

# Snow material
mat_snow = bpy.data.materials.get("Mat_SnowPure")
if not mat_snow:
    mat_snow = bpy.data.materials.new("Mat_SnowPure")
    mat_snow.use_nodes = True
    bsdf = mat_snow.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.96, 0.98, 1.0, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
if roof_snow:
    roof_snow.data.materials.clear()
    roof_snow.data.materials.append(mat_snow)
    roof_snow.hide_render = True
    roof_snow.hide_viewport = True

# Terrace snow
deck = bpy.data.objects.get("Terrace_Main_TeakDeck")
deck_snow = bpy.data.objects.get("Winter_Deck_SnowCover")
if not deck_snow and deck:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(deck.location.x, deck.location.y, deck.location.z + 0.05))
    deck_snow = bpy.context.active_object
    deck_snow.name = "Winter_Deck_SnowCover"
    deck_snow.scale = (8.90, 1.70, 0.06)
    deck_snow.data.materials.clear()
    deck_snow.data.materials.append(mat_snow)
    deck_snow.hide_render = True
    deck_snow.hide_viewport = True

# Helper functions
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

def apply_season_config(season_name):
    # Hide/show snow
    if roof_snow:
        roof_snow.hide_render = (season_name != "winter")
        roof_snow.hide_viewport = (season_name != "winter")
    if deck_snow:
        deck_snow.hide_render = (season_name != "winter")
        deck_snow.hide_viewport = (season_name != "winter")

    # Tree leaf visibility (In Winter, tree foliage is invisible, showing bare branches!)
    if mat_sakura_cloud and mat_sakura_cloud.node_tree:
        bsdf = mat_sakura_cloud.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Alpha"].default_value = 0.0 if season_name == "winter" else 1.0
        mat_sakura_cloud.blend_method = 'BLEND'

    # Foreground fluttering mesh layers (0..5)
    for i in range(6):
        fl = bpy.data.objects.get(f"Flutter_Petals_Layer_0{i}")
        if fl:
            if season_name in ["spring", "autumn", "winter"]:
                fl.hide_render = False
                fl.hide_viewport = False
            else: # Summer has clear skies, no debris
                fl.hide_render = True
                fl.hide_viewport = True

    # Particle system settings (Particle Emitter)
    if ps:
        if season_name == "summer":
            emitter.hide_render = True
            emitter.hide_viewport = True
        else:
            emitter.hide_render = False
            emitter.hide_viewport = False
            ps.settings.frame_end = 480.0
            ps.settings.lifetime = 320.0
            if season_name == "winter":
                ps.settings.particle_size = 0.40 # Fine white snow flakes
                ps.settings.size_random = 0.70
                ps.settings.effector_weights.gravity = 0.15 # Slow gentle snowfall
            elif season_name == "autumn":
                ps.settings.particle_size = 1.05 # Large vibrant maple leaves
                ps.settings.size_random = 0.50
                ps.settings.effector_weights.gravity = 0.09 # Fluttering drift
            else: # Spring
                ps.settings.particle_size = 0.85 # Delicate cherry blossom petals
                ps.settings.size_random = 0.45
                ps.settings.effector_weights.gravity = 0.08

    # Specific Season Visuals:
    if season_name == "spring":
        # Lighting: Soft golden morning sunrise
        if sky_node:
            sky_node.sun_elevation = math.radians(12.0)
            sky_node.sun_rotation = math.radians(115.0)
            sky_node.air_density = 1.05
        if sun:
            sun.data.energy = 5.2
            sun.data.color = (1.0, 0.94, 0.86)
            sun.rotation_euler = (math.radians(65.0), 0.0, math.radians(115.0))
        # Foliage: Cherry blossom pink
        set_color_ramp(mat_sakura_cloud, (0.95, 0.68, 0.78), (1.0, 0.86, 0.92))
        set_color_ramp(mat_skypark_grass, (0.18, 0.45, 0.12), (0.35, 0.65, 0.22))
        set_bsdf_color(mat_cliff_moss, (0.11, 0.27, 0.10))
        set_bsdf_color(mat_cliff_lime, (0.18, 0.36, 0.13))
        set_bsdf_color(mat_azalea, (0.94, 0.56, 0.68))
        set_color_ramp(mat_ocean, (0.01, 0.10, 0.18), (0.03, 0.24, 0.35))
        # Petals: Cherry blossom pink
        set_bsdf_color(mat_petal, (0.98, 0.76, 0.84))
        set_bsdf_color(mat_flutter, (1.0, 0.78, 0.86))
        # Interior
        if l_1f: l_1f.data.energy = 240.0
        if l_garden: l_garden.data.energy = 260.0
        if l_fire: l_fire.data.energy = 650.0

    elif season_name == "summer":
        # Lighting: Intense midday sun, clear cyan azure sky
        if sky_node:
            sky_node.sun_elevation = math.radians(68.0)
            sky_node.sun_rotation = math.radians(160.0)
            sky_node.air_density = 0.60
        if sun:
            sun.data.energy = 7.6
            sun.data.color = (1.0, 0.99, 0.96)
            sun.rotation_euler = (math.radians(22.0), 0.0, math.radians(160.0))
        # Foliage: Deep lush emerald oak green
        set_color_ramp(mat_sakura_cloud, (0.04, 0.22, 0.06), (0.12, 0.42, 0.15))
        set_color_ramp(mat_skypark_grass, (0.08, 0.38, 0.06), (0.18, 0.52, 0.14))
        set_bsdf_color(mat_cliff_moss, (0.07, 0.25, 0.08))
        set_bsdf_color(mat_cliff_lime, (0.12, 0.38, 0.10))
        set_bsdf_color(mat_azalea, (0.98, 0.20, 0.35))
        # Ocean: Sparkling turquoise tropical waters
        set_color_ramp(mat_ocean, (0.005, 0.16, 0.24), (0.02, 0.34, 0.48))
        # Interior
        if l_1f: l_1f.data.energy = 120.0
        if l_garden: l_garden.data.energy = 80.0
        if l_fire: l_fire.data.energy = 450.0

    elif season_name == "autumn":
        # Lighting: Golden hour sunset, dramatic warm orange glow
        if sky_node:
            sky_node.sun_elevation = math.radians(6.0)
            sky_node.sun_rotation = math.radians(235.0)
            sky_node.air_density = 2.2
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 2.5
        if sun:
            sun.data.energy = 8.5
            sun.data.color = (1.0, 0.46, 0.10)
            sun.rotation_euler = (math.radians(83.0), 0.0, math.radians(235.0))
        # Foliage: Scarlet crimson & amber golden maples
        set_color_ramp(mat_sakura_cloud, (0.78, 0.12, 0.02), (0.98, 0.44, 0.06))
        set_color_ramp(mat_skypark_grass, (0.48, 0.30, 0.09), (0.74, 0.50, 0.16))
        set_bsdf_color(mat_cliff_moss, (0.42, 0.28, 0.10))
        set_bsdf_color(mat_cliff_lime, (0.55, 0.38, 0.12))
        set_bsdf_color(mat_azalea, (0.90, 0.38, 0.10))
        set_color_ramp(mat_ocean, (0.02, 0.07, 0.14), (0.06, 0.20, 0.28))
        # Petals: Vibrant autumn maple leaves (Golden yellow & burnt orange-red)
        set_bsdf_color(mat_petal, (0.96, 0.32, 0.04))
        set_bsdf_color(mat_flutter, (0.92, 0.48, 0.06))
        # Interior & roaring fire
        if l_1f: l_1f.data.energy = 420.0
        if l_garden: l_garden.data.energy = 540.0
        if l_fire: l_fire.data.energy = 1100.0

    elif season_name == "winter":
        # Lighting: Cool winter light with glowing warm haven inside
        if sky_node:
            sky_node.sun_elevation = math.radians(14.0)
            sky_node.sun_rotation = math.radians(145.0)
            sky_node.air_density = 0.70
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 1.0
        if sun:
            sun.data.energy = 4.2
            sun.data.color = (0.88, 0.93, 1.0)
            sun.rotation_euler = (math.radians(60.0), 0.0, math.radians(145.0))
        # Foliage & Ground: Snow-covered white lawn & frosted landscape
        set_color_ramp(mat_skypark_grass, (0.88, 0.92, 0.96), (0.98, 0.99, 1.0))
        set_bsdf_color(mat_cliff_moss, (0.86, 0.89, 0.94))
        set_bsdf_color(mat_cliff_lime, (0.89, 0.92, 0.96))
        set_bsdf_color(mat_azalea, (0.92, 0.94, 0.97))
        set_color_ramp(mat_ocean, (0.008, 0.03, 0.07), (0.02, 0.06, 0.12))
        # Petals: PURE WHITE SNOWFLAKES falling from the sky!
        set_bsdf_color(mat_petal, (0.96, 0.98, 1.0))
        set_bsdf_color(mat_flutter, (0.95, 0.98, 1.0))
        # Tree bark dark frosty contrast
        set_bsdf_color(mat_sakura_bark, (0.12, 0.09, 0.07))
        # Interior: Max cozy fire & illumination!
        if l_1f: l_1f.data.energy = 580.0
        if l_garden: l_garden.data.energy = 680.0
        if l_fire: l_fire.data.energy = 1350.0

# Render 4 test stills at frame 220
for s in ["spring", "summer", "autumn", "winter"]:
    print(f"Testing season: {s}...")
    apply_season_config(s)
    scene.frame_set(220)
    out_file = os.path.join(TEST_DIR, f"test_{s}_f220.png")
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {out_file}")

print("ALL_4_SEASONS_TEST_RENDERED_SUCCESS")

