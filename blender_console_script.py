# Copy and paste this into Blender's Python console
# Make sure your MMD_Blender.blend file is open first

import sys
import os
import bpy

# Add the mikumotion path
mikumotion_path = "/Users/skr3178/MikuMotionTools"
if mikumotion_path not in sys.path:
    sys.path.append(mikumotion_path)

try:
    from mikumotion import blender
    from mikumotion.presets import GenericKeypointMapping
    from mikumotion.blender import (
        set_scene_animation_range,
        build_body_motion_data,
        set_armature_to_pose,
    )
    
    C = bpy.context
    D = bpy.data
    
    # Check FPS
    print(f"Current FPS: {C.scene.render.fps}")
    
    # Set motion section
    motion_section = (3000, 4000)
    set_scene_animation_range(motion_section[0], motion_section[1])
    
    # Get your armature
    source_armature = D.objects.get("TdaéÆèââπÉ~ÉNÅEÉAÉyÉìÉh Ver1.10")
    
    if source_armature is None:
        print("ERROR: Could not find armature 'TdaéÆèââπÉ~ÉNÅEÉAÉyÉìÉh Ver1.10'")
        print("Available armature objects:")
        for obj in D.objects:
            if obj.type == 'ARMATURE':
                print(f"  - {obj.name}")
    else:
        print(f"Found armature: {source_armature.name}")
        
        # Check if armature has data
        if source_armature.data is None:
            print("Armature object has no data, trying to find a working armature...")
            # Try to find another armature object that has data
            working_armature = None
            for obj in D.objects:
                if obj.type == 'ARMATURE' and obj.data is not None:
                    working_armature = obj
                    print(f"Found working armature: {obj.name}")
                    break
            
            if working_armature:
                source_armature = working_armature
                print(f"Using armature: {source_armature.name}")
            else:
                print("ERROR: Could not find any armature with data.")
                print("Available armature objects:")
                for obj in D.objects:
                    if obj.type == 'ARMATURE':
                        print(f"  - {obj.name} (data: {obj.data is not None})")
                print("Stopping execution due to missing armature data.")
                exit()
        
        print(f"Armature data: {source_armature.data.name}")
        
        # Select and make active
        bpy.context.view_layer.objects.active = source_armature
        source_armature.select_set(True)
        
        # Switch to Pose mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # Set armature to pose
        try:
            set_armature_to_pose(source_armature)
        except Exception as e:
            print(f"Warning: Could not set armature to pose: {e}")
            print("Continuing with current pose...")
        
        # Build motion data
        scaling_ratio = 0.9
        motion = build_body_motion_data(
            source_armature, 
            mapping=GenericKeypointMapping.mmd_yyb, 
            scaling_ratio=scaling_ratio
        )
        
        # Save motion data
        save_path = f"/Users/skr3178/MikuMotionTools/data/motions/mmd_motion_{motion_section[0]}_{motion_section[1]}_body_only.npz"
        motion.save(save_path)
        print(f"Results saved to {save_path}")
        
        # Fix body names for retargeting compatibility
        print("\n=== Fixing body names for retargeting compatibility ===")
        import numpy as np
        
        # Load the saved motion file
        motion_data = np.load(save_path)
        print(f"Original body names: {motion_data['body_names']}")
        
        # Convert to list to avoid numpy string length issues
        new_body_names = list(motion_data['body_names'])
        
        # Mapping from MMD names to retargeting names
        name_mapping = {
            'left_hand': 'left_rubber_hand',
            'right_hand': 'right_rubber_hand',
            'left_ankle': 'left_ankle_roll_link',
            'right_ankle': 'right_ankle_roll_link',
            'left_shoulder': 'left_shoulder_roll_link',
            'right_shoulder': 'right_shoulder_roll_link',
            'left_elbow': 'left_elbow_link',
            'right_elbow': 'right_elbow_link',
            'left_hip': 'left_hip_roll_link',
            'right_hip': 'right_hip_roll_link',
            'left_knee': 'left_knee_link',
            'right_knee': 'right_knee_link',
        }
        
        # Apply the mapping
        for i, name in enumerate(new_body_names):
            if name in name_mapping:
                new_body_names[i] = name_mapping[name]
                print(f"Renamed: {name} -> {name_mapping[name]}")
        
        # Convert back to numpy array with proper string length
        max_length = max(len(name) for name in new_body_names)
        new_body_names = np.array(new_body_names, dtype=f'U{max_length}')
        print(f"New body names: {new_body_names}")
        
        # Create new motion data with updated names
        new_motion_data = {}
        for key in motion_data.keys():
            if key == 'body_names':
                new_motion_data[key] = new_body_names
            else:
                new_motion_data[key] = motion_data[key]
        
        # Save the fixed motion file
        fixed_save_path = f"/Users/skr3178/MikuMotionTools/data/motions/mmd_motion_{motion_section[0]}_{motion_section[1]}_body_only_fixed.npz"
        np.savez(fixed_save_path, **new_motion_data)
        print(f"Fixed motion file saved to {fixed_save_path}")
        print("\n✅ Motion file is now ready for both viewing and retargeting!")

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the mikumotion package is installed in your Python environment")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
