import bpy
import bmesh
import math
from mathutils import Vector

# 1. Create realistic 5-pointed Maple Leaf geometry
def create_maple_leaf_mesh():
    mesh_name = "Maple_Leaf_Mesh"
    obj_name = "Maple_Leaf_Instance"
    
    # Remove existing if any
    old_obj = bpy.data.objects.get(obj_name)
    if old_obj:
        bpy.data.objects.remove(old_obj, do_unlink=True)
    old_mesh = bpy.data.meshes.get(mesh_name)
    if old_mesh:
        bpy.data.meshes.remove(old_mesh)
        
    bm = bmesh.new()
    
    # Points defining a Japanese maple leaf silhouette (5 lobes + stem)
    # Stem: (0, -0.06) -> base (0, 0)
    # Lobes: Bottom Left, Top Left, Center Tip, Top Right, Bottom Right
    verts = [
        # 0: Leaf base
        bm.verts.new((0.0, 0.0, 0.0)),
        # 1: Stem tip
        bm.verts.new((0.0, -0.05, 0.002)),
        # 2: Left bottom notch
        bm.verts.new((-0.02, 0.01, 0.003)),
        # 3: Left bottom lobe tip
        bm.verts.new((-0.07, 0.02, 0.008)),
        # 4: Left mid notch
        bm.verts.new((-0.04, 0.045, 0.005)),
        # 5: Left top lobe tip
        bm.verts.new((-0.075, 0.085, 0.012)),
        # 6: Left high notch
        bm.verts.new((-0.03, 0.08, 0.006)),
        # 7: Center top lobe tip (tallest)
        bm.verts.new((0.0, 0.12, 0.015)),
        # 8: Right high notch
        bm.verts.new((0.03, 0.08, 0.006)),
        # 9: Right top lobe tip
        bm.verts.new((0.075, 0.085, 0.012)),
        # 10: Right mid notch
        bm.verts.new((0.04, 0.045, 0.005)),
        # 11: Right bottom lobe tip
        bm.verts.new((0.07, 0.02, 0.008)),
        # 12: Right bottom notch
        bm.verts.new((0.02, 0.01, 0.003)),
        # 13: Mid center rib
        bm.verts.new((0.0, 0.05, 0.008))
    ]
    bm.verts.ensure_lookup_table()
    
    # Faces
    # Stem
    # bm.faces.new([verts[1], verts[0]]) -> edge
    # Leaf triangles from center
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
    bm.faces.new([b, verts[12], verts[0]])
    
    mesh = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = (0, 0, -20) # Out of direct view
    
    # Solidify modifier for subtle thickness
    mod = obj.modifiers.new(name="LeafThickness", type='SOLIDIFY')
    mod.thickness = 0.002
    
    # Maple leaf material: rich scarlet red and burnt amber with vein translucency
    mat = bpy.data.materials.get("Mat_MapleLeafAutumn")
    if not mat:
        mat = bpy.data.materials.new("Mat_MapleLeafAutumn")
        mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.12, 0.02, 1.0) # Vivid crimson red
    bsdf.inputs['Roughness'].default_value = 0.45
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.35
        bsdf.inputs['Subsurface Radius'].default_value = (0.8, 0.2, 0.05)
    
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    print("Created Maple Leaf instance:", obj.name)
    return obj

create_maple_leaf_mesh()

