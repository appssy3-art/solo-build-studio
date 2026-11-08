import bpy
import bmesh
import math
import os
from mathutils import Vector

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
TEST_DIR = os.path.join(ROOT, "scratch", "seasonal_tests_v4")
os.makedirs(TEST_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene
world = scene.world

# 1. PERMANENTLY NORMALIZE OCEAN VERTICES
ocean = bpy.data.objects.get("Ocean_Surface")
if ocean:
    mesh = ocean.data
    # Check if vertices need shifting
    zs = [v.co.z for v in mesh.vertices]
    mean_z = sum(zs) / len(zs)
    print(f"Current ocean vertex mean Z: {mean_z:.3f}")
    if mean_z < -2.0:
        offset = -mean_z
        for v in mesh.vertices:
            v.co.z += offset
        mesh.update()
        print(f"Shifted ocean vertices by {offset:.3f}m to normalize to Z=0")
    
    # Place ocean surface at Z = -1.1m (just below cliff terrace base at 0.0m)
    ocean.location = (0.0, 0.0, -1.1)
    ocean.scale = (4.0, 4.0, 1.0)
    print("Ocean positioned at:", ocean.location, "scale:", ocean.scale)

# 2. OCEAN SHADER: HIGH-CONTRAST COASTAL WATER WITH WAVES & FOAM
mat_ocean = bpy.data.materials.get("Mat_OceanSparkle")
if mat_ocean and mat_ocean.node_tree:
    nodes = mat_ocean.node_tree.nodes
    links = mat_ocean.node_tree.links
    nodes.clear()
    
    out_node = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    
    noise_wave = nodes.new('ShaderNodeTexNoise')
    noise_wave.name = "Noise_Wave"
    noise_wave.inputs['Scale'].default_value = 12.0
    noise_wave.inputs['Detail'].default_value = 5.0
    noise_wave.inputs['Roughness'].default_value = 0.55
    
    noise_foam = nodes.new('ShaderNodeTexNoise')
    noise_foam.name = "Noise_Foam"
    noise_foam.inputs['Scale'].default_value = 28.0
    noise_foam.inputs['Detail'].default_value = 8.0
    
    cramp_sea = nodes.new('ShaderNodeValToRGB')
    cramp_sea.name = "Color Ramp"
    cramp_sea.color_ramp.elements[0].position = 0.2
    cramp_sea.color_ramp.elements[0].color = (0.01, 0.52, 0.72, 1.0) # Vivid Turquoise
    cramp_sea.color_ramp.elements[1].position = 0.8
    cramp_sea.color_ramp.elements[1].color = (0.005, 0.16, 0.46, 1.0) # Deep Azure
    
    cramp_foam = nodes.new('ShaderNodeValToRGB')
    cramp_foam.name = "Foam_Ramp"
    cramp_foam.color_ramp.elements[0].position = 0.68
    cramp_foam.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cramp_foam.color_ramp.elements[1].position = 0.76
    cramp_foam.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0) # Crisp White Foam
    
    mix_foam = nodes.new('ShaderNodeMix')
    mix_foam.name = "Mix_Foam"
    mix_foam.data_type = 'RGBA'
    
    white_foam = nodes.new('ShaderNodeRGB')
    white_foam.outputs['Color'].default_value = (0.96, 0.98, 1.0, 1.0)
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.40
    bump.inputs['Distance'].default_value = 0.15
    
    links.new(tex_coord.outputs['Generated'], noise_wave.inputs['Vector'])
    links.new(tex_coord.outputs['Generated'], noise_foam.inputs['Vector'])
    links.new(noise_wave.outputs['Fac'], cramp_sea.inputs['Fac'])
    links.new(noise_foam.outputs['Fac'], cramp_foam.inputs['Fac'])
    
    links.new(cramp_foam.outputs['Color'], mix_foam.inputs['Factor'])
    links.new(cramp_sea.outputs['Color'], mix_foam.inputs['A'])
    links.new(white_foam.outputs['Color'], mix_foam.inputs['B'])
    
    links.new(mix_foam.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.12
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.10
    bsdf.inputs['IOR'].default_value = 1.333
    
    links.new(noise_wave.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

# 3. FIX TREE EMISSION ARTIFACT IN Mat_SakuraCloud
mat_sakura_cloud = bpy.data.materials.get("Mat_SakuraCloud")
if mat_sakura_cloud and mat_sakura_cloud.node_tree:
    bsdf = mat_sakura_cloud.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Strength"].default_value = 0.0 # Remove pink glow!
        bsdf.inputs["Emission Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = 0.20

# 4. TUNE FIREPLACE MATERIALS FOR RICH ORANGE/RED EMBERS & FLAMES
mat_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
if mat_core and mat_core.node_tree:
    bsdf = mat_core.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (1.0, 0.50, 0.05, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.65, 0.08, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 35.0

mat_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
if mat_outer and mat_outer.node_tree:
    bsdf = mat_outer.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.15, 0.01, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.22, 0.01, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 22.0

mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")
if mat_ember and mat_ember.node_tree:
    bsdf = mat_ember.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.2, 0.02, 0.005, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.10, 0.005, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 45.0

l_fire = bpy.data.objects.get("Light_1F_FireplacePointGlow")
if l_fire:
    l_fire.location = (0.95, -0.30, 0.90)
    l_fire.data.shadow_soft_size = 0.65
    l_fire.data.color = (1.0, 0.38, 0.04)

# Save changes to master blend file
bpy.ops.wm.save_mainfile(filepath=BLEND_FILE)
print("Base master blend file upgraded and saved!")

