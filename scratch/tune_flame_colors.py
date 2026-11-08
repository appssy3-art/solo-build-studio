import bpy
import math

BLEND_FILE = r"E:\ai랩\AI자율회사만들기\solo_build_cliffside_drone_13s.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

# Adjust flame emission to prevent blowout and show rich fiery warmth
mat_core = bpy.data.materials.get("Mat_FlameCoreWhiteYellow")
if mat_core and mat_core.node_tree:
    bsdf = mat_core.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.65, 0.12, 1.0) # Warm gold-amber core
        bsdf.inputs["Emission Strength"].default_value = 45.0

mat_outer = bpy.data.materials.get("Mat_FlameOuterVividOrange")
if mat_outer and mat_outer.node_tree:
    bsdf = mat_outer.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.28, 0.02, 1.0) # Deep fiery crimson-orange
        bsdf.inputs["Emission Strength"].default_value = 32.0

mat_ember = bpy.data.materials.get("Mat_FireEmbersGlow")
if mat_ember and mat_ember.node_tree:
    bsdf = mat_ember.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.15, 0.01, 1.0) # Glowing red-hot coals
        bsdf.inputs["Emission Strength"].default_value = 35.0

# Light tuning: Fireplace point light warm flickery glow
lfire1 = bpy.data.objects.get("Light_1F_FireplacePointGlow")
if lfire1:
    lfire1.data.energy = 850.0
    lfire1.data.color = (1.0, 0.42, 0.08)

bpy.ops.wm.save_mainfile()
print("FIRE_COLORS_TUNED_SUCCESS")

scene = bpy.context.scene
scene.frame_set(220)
test_out = r"E:\ai랩\AI자율회사만들기\scratch\test_fireplace_flame_tuned.png"
scene.render.filepath = test_out
bpy.ops.render.render(write_still=True)
print("TEST_FLAME_TUNED_RENDERED:", test_out)

