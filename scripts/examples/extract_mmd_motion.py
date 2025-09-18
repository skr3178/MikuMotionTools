"""
Extract motion data from MMD Blender file with Tda Miku model.

Usage:
```bash
blender "MikuMiku Dance/Blender/MMD_Blender.blend" --python ./scripts/examples/extract_mmd_motion.py
```
"""

import sys
import os
import bpy
import importlib

""" Include the pose library """

blend_path = os.path.dirname(bpy.data.filepath)
mikumotion_path = os.getcwd()

if blend_path not in sys.path:
   sys.path.append(blend_path)

if mikumotion_path not in sys.path:
   sys.path.append(mikumotion_path)

from mikumotion import blender

importlib.reload(blender)

C = bpy.context
D = bpy.data
O = bpy.ops


""" Everything else follows """

import numpy as np
from mikumotion.presets import GenericKeypointMapping
from mikumotion.blender import (
    set_scene_animation_range,
    build_body_motion_data,
    set_armature_to_rest,
    set_armature_to_pose,
)
from mikumotion.math import quat_mul, quat_from_euler_xyz


# Check FPS - MMD typically uses 30fps, but let's be flexible
print(f"Current FPS: {C.scene.render.fps}")

# motion_section = (0, 1632)
motion_section = (0, 600)

set_scene_animation_range(motion_section[0], motion_section[1])

# Use your armature name
source_armature = D.objects.get("TdaéÆèââπÉ~ÉNÅEÉAÉyÉìÉh Ver1.10")

if source_armature is None:
    print("ERROR: Could not find armature 'TdaéÆèââπÉ~ÉNÅEÉAÉyÉìÉh Ver1.10'")
    print("Available objects:")
    for obj in D.objects:
        if obj.type == 'ARMATURE':
            print(f"  - {obj.name}")
    sys.exit(1)

print(f"Found armature: {source_armature.name}")

# set_armature_to_rest(source_armature)
set_armature_to_pose(source_armature)

scaling_ratio = 0.9

motion = build_body_motion_data(source_armature, mapping=GenericKeypointMapping.mmd_yyb, scaling_ratio=scaling_ratio)

save_path = f"./data/motions/mmd_motion_{motion_section[0]}_{motion_section[1]}_body_only.npz"
motion.save(save_path)
print(f"Results saved to {save_path}")
