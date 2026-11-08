import bpy

scene = bpy.context.scene
print("=== VIEW SETTINGS ===")
print("View transform:", scene.view_settings.view_transform)
print("Look:", scene.view_settings.look)
print("Exposure:", scene.view_settings.exposure)
print("Gamma:", scene.view_settings.gamma)

print("\n=== OCEAN SURFACE ===")
ocean = bpy.data.objects.get("Ocean_Surface")
if ocean:
    print("Ocean location:", ocean.location)
    print("Ocean dimensions:", ocean.dimensions)
    print("Ocean scale:", ocean.scale)
    for m in ocean.data.materials:
        if m:
            print("Ocean mat:", m.name)
            if m.node_tree:
                for node in m.node_tree.nodes:
                    print("  Node:", node.name, node.type)
                    if node.type == 'BSDF_PRINCIPLED':
                        print("    Base Color:", [round(x, 3) for x in node.inputs['Base Color'].default_value])
                        print("    Roughness:", round(node.inputs['Roughness'].default_value, 3))
                        if 'Transmission Weight' in node.inputs:
                            print("    Transmission Weight:", round(node.inputs['Transmission Weight'].default_value, 3))
                        print("    IOR:", round(node.inputs['IOR'].default_value, 3))

print("\n=== FIREPLACE OBJECTS ===")
fp_objs = [o.name for o in bpy.data.objects if any(k in o.name.lower() for k in ['fire', 'flame', 'hearth', 'log', 'ember'])]
print("Fireplace related objects:", fp_objs)
for name in fp_objs:
    o = bpy.data.objects[name]
    print(f"  {name}: loc={o.location}, hide_render={o.hide_render}, type={o.type}")
    if o.type == 'LIGHT':
        print(f"    Light energy={o.data.energy}, color={[round(c, 3) for c in o.data.color]}")
    elif o.data and hasattr(o.data, 'materials'):
        for m in o.data.materials:
            if m and m.node_tree:
                bsdf = m.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    print(f"    Mat {m.name} BSDF: Base={[round(c, 3) for c in bsdf.inputs['Base Color'].default_value]}")
                    if 'Emission Color' in bsdf.inputs:
                        print(f"      Emission Color={[round(c, 3) for c in bsdf.inputs['Emission Color'].default_value]}, Strength={round(bsdf.inputs['Emission Strength'].default_value, 1)}")

print("\n=== WORLD NODES ===")
if scene.world and scene.world.node_tree:
    for n in scene.world.node_tree.nodes:
        print("World node:", n.name, n.type)
        if n.type == 'TEX_SKY':
            print("  Sky model:", getattr(n, 'sky_model', 'N/A'))
            print("  Sun elevation:", getattr(n, 'sun_elevation', 0))
            print("  Sun rotation:", getattr(n, 'sun_rotation', 0))
            print("  Air density:", getattr(n, 'air_density', 0))
            print("  Dust density:", getattr(n, 'dust_density', 0))
            print("  Ozone density:", getattr(n, 'ozone_density', 0))
        elif n.type == 'BACKGROUND':
            print("  Background strength:", n.inputs['Strength'].default_value)
            print("  Background color:", [round(c, 3) for c in n.inputs['Color'].default_value])

print("\n=== PARTICLES & SAKURA ===")
emitter = bpy.data.objects.get("Petal_Emitter_Canopy")
if emitter and emitter.particle_systems:
    for ps in emitter.particle_systems:
        print("PS:", ps.name, "instance_object:", getattr(ps.settings, 'instance_object', None))

