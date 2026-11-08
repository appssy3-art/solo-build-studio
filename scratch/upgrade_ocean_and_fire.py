import bpy
import bmesh
import math
import os
from mathutils import Vector

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene
world = scene.world

# 1. CREATE DISTINCT MAPLE LEAF OBJECT
def setup_maple_leaf():
    mesh_name = "Maple_Leaf_Mesh"
    obj_name = "Maple_Leaf_Instance"
    old_obj = bpy.data.objects.get(obj_name)
    if old_obj:
        bpy.data.objects.remove(old_obj, do_unlink=True)
    old_mesh = bpy.data.meshes.get(mesh_name)
    if old_mesh:
        bpy.data.meshes.remove(old_mesh)
        
    bm = bmesh.new()
    verts = [
        bm.verts.new((0.0, 0.0, 0.0)),            # 0
        bm.verts.new((0.0, -0.06, 0.002)),        # 1 stem
        bm.verts.new((-0.03, 0.015, 0.003)),      # 2
        bm.verts.new((-0.09, 0.03, 0.008)),       # 3 lobe left bottom
        bm.verts.new((-0.05, 0.06, 0.005)),       # 4
        bm.verts.new((-0.10, 0.11, 0.012)),       # 5 lobe left top
        bm.verts.new((-0.04, 0.11, 0.006)),       # 6
        bm.verts.new((0.0, 0.16, 0.015)),         # 7 lobe center top
        bm.verts.new((0.04, 0.11, 0.006)),        # 8
        bm.verts.new((0.10, 0.11, 0.012)),        # 9 lobe right top
        bm.verts.new((0.05, 0.06, 0.005)),        # 10
        bm.verts.new((0.09, 0.03, 0.008)),        # 11 lobe right bottom
        bm.verts.new((0.03, 0.015, 0.003)),       # 12
        bm.verts.new((0.0, 0.07, 0.008))          # 13 mid center
    ]
    bm.verts.ensure_lookup_table()
    c = verts[13]
    b = verts[0]
    bm.faces.new([b, verts[2], verts[3]])
    bm.faces.new([b, verts[3], verts[4]])
    bm.faces.new([b, verts[4], c])
    bm.faces.new([c, verts[4], verts[5]])
    bm.faces.new([c, verts[5], verts[6]])
    bm.faces.new([c, verts[6], verts[7]])
    bm.faces.new([c, verts[7], verts[8]])
    bm.faces.new([c, verts[8], verts[9]])
    bm.faces.new([c, verts[9], verts[10]])
    bm.faces.new([b, c, verts[10]])
    bm.faces.new([b, verts[10], verts[11]])
    bm.faces.new([b, verts[11], verts[12]])
    bm.faces.new([b, verts[12], verts[2]])
    
    mesh = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(obj_name, mesh)
    scene.collection.objects.link(obj)
    obj.location = (0, 0, -25)
    
    mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod.thickness = 0.003
    
    mat = bpy.data.materials.get("Mat_MapleLeafAutumn")
    if not mat:
        mat = bpy.data.materials.new("Mat_MapleLeafAutumn")
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out_node = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.18, 0.02, 1.0) # Vivid scarlet maple
    bsdf.inputs['Roughness'].default_value = 0.4
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.4
        bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.3, 0.05)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

setup_maple_leaf()

# 2. UPGRADE OCEAN GEOMETRY & SHADER
ocean = bpy.data.objects.get("Ocean_Surface")
if ocean:
    ocean.location = (0.0, -10.0, -1.6) # Raised up so water meets cliff base!
    ocean.scale = (3.0, 3.0, 1.0)      # Expansive coverage
    
    mat_ocean = bpy.data.materials.get("Mat_OceanSparkle")
    if mat_ocean and mat_ocean.node_tree:
        nodes = mat_ocean.node_tree.nodes
        links = mat_ocean.node_tree.links
        nodes.clear()
        
        out_node = nodes.new('ShaderNodeOutputMaterial')
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        tex_coord = nodes.new('ShaderNodeTexCoord')
        noise_wave = nodes.new('ShaderNodeTexNoise')
        noise_wave.inputs['Scale'].default_value = 8.0
        noise_wave.inputs['Detail'].default_value = 6.0
        noise_wave.inputs['Roughness'].default_value = 0.65
        
        noise_foam = nodes.new('ShaderNodeTexNoise')
        noise_foam.inputs['Scale'].default_value = 24.0
        noise_foam.inputs['Detail'].default_value = 8.0
        
        # Color Ramp for coastal water depth / waves
        cramp_sea = nodes.new('ShaderNodeValToRGB')
        cramp_sea.name = "Color Ramp"
        cramp_sea.color_ramp.elements[0].position = 0.25
        cramp_sea.color_ramp.elements[0].color = (0.01, 0.45, 0.65, 1.0) # Tropical Turquoise / Cyan
        cramp_sea.color_ramp.elements[1].position = 0.85
        cramp_sea.color_ramp.elements[1].color = (0.005, 0.18, 0.45, 1.0) # Deep Azure Blue
        
        # Foam mix
        cramp_foam = nodes.new('ShaderNodeValToRGB')
        cramp_foam.color_ramp.elements[0].position = 0.72
        cramp_foam.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        cramp_foam.color_ramp.elements[1].position = 0.78
        cramp_foam.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0) # Crisp white sea foam
        
        mix_rgb = nodes.new('ShaderNodeMix')
        mix_rgb.data_type = 'RGBA'
        
        # Bump for visible 3D water waves
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.45
        bump.inputs['Distance'].default_value = 0.12
        
        links.new(tex_coord.outputs['Generated'], noise_wave.inputs['Vector'])
        links.new(tex_coord.outputs['Generated'], noise_foam.inputs['Vector'])
        links.new(noise_wave.outputs['Fac'], cramp_sea.inputs['Fac'])
        links.new(noise_foam.outputs['Fac'], cramp_foam.inputs['Fac'])
        
        links.new(cramp_foam.outputs['Color'], mix_rgb.inputs['Factor'])
        links.new(cramp_sea.outputs['Color'], mix_rgb.inputs['A'])
        # Bright white foam crest
        white_val = nodes.new('ShaderNodeRGB')
        white_val.outputs['Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        links.new(white_val.outputs['Color'], mix_rgb.inputs['B'])
        
        links.new(mix_rgb.outputs['Result'], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.18
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.15
        bsdf.inputs['IOR'].default_value = 1.333
        
        links.new(noise_wave.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

# 3. UPGRADE FIREPLACE MATERIALS & FLAME GLOW
mat_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
if mat_core and mat_core.node_tree:
    bsdf = mat_core.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.65, 0.08, 1.0) # Blazing fire amber
        bsdf.inputs['Emission Strength'].default_value = 140.0

mat_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
if mat_outer and mat_outer.node_tree:
    bsdf = mat_outer.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.22, 0.01, 1.0) # Deep fiery red-orange
        bsdf.inputs['Emission Strength'].default_value = 95.0

mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")
if mat_ember and mat_ember.node_tree:
    bsdf = mat_ember.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.02, 0.005, 0.0, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.14, 0.01, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 60.0

# Adjust Light_1F_FireplacePointGlow position and soft radius
l_fire = bpy.data.objects.get("Light_1F_FireplacePointGlow")
if l_fire:
    l_fire.location = (0.95, -0.15, 0.95) # Moved forward into living room
    l_fire.data.shadow_soft_size = 0.55
    l_fire.data.color = (1.0, 0.38, 0.05)

# 4. Save updated master blend file
bpy.ops.wm.save_mainfile(filepath=BLEND_FILE)
print("Updated master blend file saved successfully!")
