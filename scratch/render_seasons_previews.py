"""Accurate 4 Seasons (Spring, Summer, Autumn, Winter) rendering script."""
import bpy
import math
import os

scene = bpy.context.scene
world = scene.world
sky_node = world.node_tree.nodes.get("Sky Texture") if (world and world.node_tree) else None
sun = bpy.data.objects.get("Sun_SpringMorning")

out_dir = r"E:\ai랩\AI자율회사만들기\seasons_preview"
os.makedirs(out_dir, exist_ok=True)

mat_sakura_cloud = bpy.data.materials.get("Mat_SakuraCloud")
mat_skypark_grass = bpy.data.materials.get("Mat_SkyparkGrass")
mat_cliff_moss = bpy.data.materials.get("Mat_CliffVelvetMoss")
mat_cliff_lime = bpy.data.materials.get("Mat_CliffLimeMoss")
mat_azalea = bpy.data.materials.get("Mat_CliffAzaleaPink")
mat_ocean = bpy.data.materials.get("Mat_OceanSparkle")

def set_color_ramp(mat, stop0_col, stop1_col):
    if not mat or not mat.node_tree: return
    cramp = mat.node_tree.nodes.get("Color Ramp")
    if cramp:
        cramp.color_ramp.elements[0].color = (*stop0_col, 1.0)
        cramp.color_ramp.elements[1].color = (*stop1_col, 1.0)
    else:
        # If no Color Ramp, set Principled BSDF directly
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf and not bsdf.inputs["Base Color"].is_linked:
            bsdf.inputs["Base Color"].default_value = (*stop0_col, 1.0)

def set_bsdf_color(mat, col):
    if not mat or not mat.node_tree: return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*col, 1.0)

def apply_season(season):
    l_1f = bpy.data.objects.get("Light_1F_LobbyWarmFill")
    l_garden = bpy.data.objects.get("Light_CliffGardenWarmGlow")
    
    if season == "spring":
        # 1. Spring: Soft pastel cherry blossoms, fresh spring lawn, morning golden light
        if sky_node:
            sky_node.sun_elevation = math.radians(12.0)
            sky_node.sun_rotation = math.radians(115.0)
            sky_node.air_density = 1.0
        if sun:
            sun.data.energy = 4.8
            sun.data.color = (1.0, 0.94, 0.85)
            sun.rotation_euler = (math.radians(65.0), 0.0, math.radians(115.0))
        # Cherry blossom pink gradient
        set_color_ramp(mat_sakura_cloud, (0.95, 0.68, 0.78), (1.0, 0.86, 0.92))
        set_color_ramp(mat_skypark_grass, (0.18, 0.45, 0.12), (0.35, 0.65, 0.22))
        set_bsdf_color(mat_cliff_moss, (0.11, 0.27, 0.10))
        set_bsdf_color(mat_cliff_lime, (0.18, 0.36, 0.13))
        set_bsdf_color(mat_azalea, (0.94, 0.56, 0.68))
        if l_1f: l_1f.data.energy = 220.0
        if l_garden: l_garden.data.energy = 280.0
        
    elif season == "summer":
        # 2. Summer: Deep rich emerald green trees, vivid cyan-turquoise ocean, high midday sun
        if sky_node:
            sky_node.sun_elevation = math.radians(65.0)
            sky_node.sun_rotation = math.radians(160.0)
            sky_node.air_density = 0.65
        if sun:
            sun.data.energy = 7.2
            sun.data.color = (1.0, 0.99, 0.96)
            sun.rotation_euler = (math.radians(25.0), 0.0, math.radians(160.0))
        # Deep lush emerald green canopy
        set_color_ramp(mat_sakura_cloud, (0.04, 0.22, 0.06), (0.12, 0.42, 0.15))
        set_color_ramp(mat_skypark_grass, (0.08, 0.38, 0.06), (0.18, 0.52, 0.14))
        set_bsdf_color(mat_cliff_moss, (0.07, 0.25, 0.08))
        set_bsdf_color(mat_cliff_lime, (0.12, 0.38, 0.10))
        set_bsdf_color(mat_azalea, (0.98, 0.22, 0.35))
        set_color_ramp(mat_ocean, (0.005, 0.15, 0.22), (0.02, 0.32, 0.45))
        if l_1f: l_1f.data.energy = 100.0
        if l_garden: l_garden.data.energy = 60.0
        
    elif season == "autumn":
        # 3. Autumn: Fiery scarlet & vibrant golden-orange maples, warm amber grass & moss, dusk sunset
        if sky_node:
            sky_node.sun_elevation = math.radians(6.5)
            sky_node.sun_rotation = math.radians(235.0)
            sky_node.air_density = 2.0
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 2.5
        if sun:
            sun.data.energy = 7.5
            sun.data.color = (1.0, 0.50, 0.15)
            sun.rotation_euler = (math.radians(82.0), 0.0, math.radians(235.0))
        # Brilliant Japanese Maple Crimson & Golden Amber
        set_color_ramp(mat_sakura_cloud, (0.75, 0.12, 0.03), (0.98, 0.42, 0.06))
        set_color_ramp(mat_skypark_grass, (0.48, 0.30, 0.10), (0.72, 0.48, 0.16))
        set_bsdf_color(mat_cliff_moss, (0.42, 0.28, 0.10))
        set_bsdf_color(mat_cliff_lime, (0.55, 0.38, 0.12))
        set_bsdf_color(mat_azalea, (0.88, 0.38, 0.10))
        if l_1f: l_1f.data.energy = 360.0
        if l_garden: l_garden.data.energy = 480.0
        
    elif season == "winter":
        # 4. Winter: Crisp pure white snow on trees & roof, frosty cool lighting, glowing warm fireplace
        if sky_node:
            sky_node.sun_elevation = math.radians(16.0)
            sky_node.sun_rotation = math.radians(145.0)
            sky_node.air_density = 0.70
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 1.0
        if sun:
            sun.data.energy = 4.0
            sun.data.color = (0.90, 0.94, 1.0)
            sun.rotation_euler = (math.radians(58.0), 0.0, math.radians(145.0))
        # Pure White Snow with soft icy cyan shadows
        set_color_ramp(mat_sakura_cloud, (0.88, 0.92, 0.96), (0.98, 0.99, 1.0))
        set_color_ramp(mat_skypark_grass, (0.86, 0.90, 0.95), (0.97, 0.98, 1.0))
        set_bsdf_color(mat_cliff_moss, (0.85, 0.88, 0.92))
        set_bsdf_color(mat_cliff_lime, (0.88, 0.91, 0.95))
        set_bsdf_color(mat_azalea, (0.90, 0.92, 0.96))
        set_color_ramp(mat_ocean, (0.008, 0.03, 0.07), (0.02, 0.06, 0.12))
        if l_1f: l_1f.data.energy = 540.0
        if l_garden: l_garden.data.energy = 680.0

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.frame_set(192)

for s in ["spring", "summer", "autumn", "winter"]:
    apply_season(s)
    scene.render.filepath = os.path.join(out_dir, f"season_{s}.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered season:", s)

apply_season("spring")
print("ALL_SEASONS_RENDERED_SUCCESS")
