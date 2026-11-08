import bpy
import math
import os

ROOT = r"E:\ai랩\AI자율회사만들기"
BLEND_FILE = os.path.join(ROOT, "solo_build_cliffside_drone_13s.blend")
TEST_DIR = os.path.join(ROOT, "scratch", "test_stair_fix")
os.makedirs(TEST_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
scene = bpy.context.scene

# Set Ocean to Z = -3.8m (strictly below all 26 stairs)
ocean = bpy.data.objects.get("Ocean_Surface")
if ocean:
    ocean.location = (0.0, 0.0, -3.8)
    ocean.scale = (5.0, 5.0, 1.0) # Vast expanse to the horizon

# Summer look test
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Frame 0: Right in front of entrance stairs
scene.frame_set(0)
out_f0 = os.path.join(TEST_DIR, "test_stairs_f0.png")
scene.render.filepath = out_f0
bpy.ops.render.render(write_still=True)
print(f"Rendered Frame 0: {out_f0}")

# Frame 50: Ascending stairs
scene.frame_set(50)
out_f50 = os.path.join(TEST_DIR, "test_stairs_f50.png")
scene.render.filepath = out_f50
bpy.ops.render.render(write_still=True)
print(f"Rendered Frame 50: {out_f50}")

# Frame 220: Front drone view
scene.frame_set(220)
out_f220 = os.path.join(TEST_DIR, "test_front_f220.png")
scene.render.filepath = out_f220
bpy.ops.render.render(write_still=True)
print(f"Rendered Frame 220: {out_f220}")

