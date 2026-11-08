"""Preview 4 times of day (Morning, Noon, Sunset, Night) for SOLO BUILD Studio in Blender."""
import bpy
import math
import os
from mathutils import Vector, Euler

scene = bpy.context.scene
world = scene.world
sky_node = world.node_tree.nodes.get("Sky Texture") if (world and world.node_tree) else None
bg_node = world.node_tree.nodes.get("Background") if (world and world.node_tree) else None
sun = bpy.data.objects.get("Sun_SpringMorning")

out_dir = r"E:\ai랩\AI자율회사만들기\seasons_preview"
os.makedirs(out_dir, exist_ok=True)

def set_time_of_day(time_name):
    l_1f = bpy.data.objects.get("Light_1F_LobbyWarmFill")
    l_garden = bpy.data.objects.get("Light_CliffGardenWarmGlow")
    
    if time_name == "morning":  # Clear fresh morning
        if sky_node:
            sky_node.sun_elevation = math.radians(10.0)
            sky_node.sun_rotation = math.radians(115.0)
            sky_node.altitude = 120.0
            sky_node.air_density = 1.0
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 1.0
        if sun:
            sun.data.energy = 4.5
            sun.data.color = (1.0, 0.94, 0.85)
            sun.rotation_euler = (math.radians(65.0), 0.0, math.radians(115.0))
        if l_1f: l_1f.data.energy = 220.0
        if l_garden: l_garden.data.energy = 280.0
        
    elif time_name == "noon":  # Crisp midday, clear blue sky, vivid turquoise ocean
        if sky_node:
            sky_node.sun_elevation = math.radians(68.0)
            sky_node.sun_rotation = math.radians(180.0)
            sky_node.altitude = 250.0
            sky_node.air_density = 0.7
        if sun:
            sun.data.energy = 6.5
            sun.data.color = (1.0, 0.98, 0.95)
            sun.rotation_euler = (math.radians(22.0), 0.0, math.radians(180.0))
        if l_1f: l_1f.data.energy = 100.0
        if l_garden: l_garden.data.energy = 50.0
        
    elif time_name == "sunset":  # Golden hour, dramatic long shadows, deep amber/crimson sky
        if sky_node:
            sky_node.sun_elevation = math.radians(4.0)
            sky_node.sun_rotation = math.radians(245.0)
            sky_node.altitude = 40.0
            sky_node.air_density = 2.2
            if hasattr(sky_node, 'ozone_density'): sky_node.ozone_density = 2.5
        if sun:
            sun.data.energy = 8.0
            sun.data.color = (1.0, 0.45, 0.14)
            sun.rotation_euler = (math.radians(84.0), 0.0, math.radians(245.0))
        if l_1f: l_1f.data.energy = 380.0
        if l_garden: l_garden.data.energy = 520.0
        
    elif time_name == "night":  # Blue hour / Midnight with warm architectural illumination
        if sky_node:
            sky_node.sun_elevation = math.radians(-12.0)
            sky_node.sun_rotation = math.radians(0.0)
            sky_node.air_density = 1.0
        if bg_node:
            bg_node.inputs['Color'].default_value = (0.012, 0.022, 0.045, 1.0)
            bg_node.inputs['Strength'].default_value = 0.55
        if sun:
            sun.data.energy = 0.45  # Cool moonlight
            sun.data.color = (0.45, 0.65, 1.0)
            sun.rotation_euler = (math.radians(45.0), 0.0, math.radians(40.0))
        if l_1f: l_1f.data.energy = 450.0
        if l_garden: l_garden.data.energy = 620.0

# Render 16:9 widescreen stills (1280x720) at frame 192 for fast preview
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.frame_set(192)

for tod in ["morning", "noon", "sunset", "night"]:
    set_time_of_day(tod)
    scene.render.filepath = os.path.join(out_dir, f"time_{tod}.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered:", tod)

print("ALL_TOD_RENDERED_OK")
