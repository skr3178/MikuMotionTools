#!/usr/bin/env python3
"""
Simple MuJoCo viewer for G1 robot motion data.
"""

import mujoco
import numpy as np
import time

def view_g1_motion(motion_file):
    """View G1 robot motion in MuJoCo."""
    
    # Load the motion data
    motion_data = np.load(motion_file)
    print(f"Motion loaded: {motion_file}")
    print(f"Duration: {len(motion_data['dof_positions']) / motion_data['fps'][0]:.2f} seconds")
    print(f"Frames: {len(motion_data['dof_positions'])}")
    print(f"FPS: {motion_data['fps'][0]}")
    
    # Load the G1 robot model
    robot_xml = "./data/robots/unitree/g1/mjcf/g1_29dof_mode_5_mocap.xml"
    model = mujoco.MjModel.from_xml_path(robot_xml)
    data = mujoco.MjData(model)
    
    # Create viewer using the correct MuJoCo API
    try:
        # Try the newer MuJoCo viewer API (MuJoCo 3.0+)
        from mujoco import viewer
        with viewer.launch_passive(model, data) as viewer_obj:
            print("MuJoCo viewer launched! Press Ctrl+C to exit.")
            play_motion(model, data, motion_data, viewer_obj)
    except (ImportError, AttributeError, RuntimeError) as e:
        # Fallback: Use basic rendering without viewer
        print(f"Viewer not available ({e}), using basic mode...")
        play_motion_basic(model, data, motion_data)

def play_motion(model, data, motion_data, viewer_obj):
    """Play motion with MuJoCo viewer."""
    frame = 0
    while viewer_obj.is_running():
        # Set joint positions from motion data
        if frame < len(motion_data['dof_positions']):
            data.qpos[:] = motion_data['dof_positions'][frame]
            data.qvel[:] = motion_data['dof_velocities'][frame]
            
            # Forward dynamics
            mujoco.mj_forward(model, data)
            
            # Update viewer
            viewer_obj.sync()
            
            # Next frame
            frame += 1
        else:
            # Loop back to beginning
            frame = 0
        
        # Control playback speed
        time.sleep(1.0 / motion_data['fps'][0])

def play_motion_basic(model, data, motion_data):
    """Play motion with basic MuJoCo rendering."""
    print("Playing motion (basic mode)...")
    print(f"Model DOF: {model.nq}, Motion DOF: {motion_data['dof_positions'].shape[1]}")
    
    frame = 0
    while frame < len(motion_data['dof_positions']):
        # Set joint positions from motion data
        # The model has more DOF than the motion (floating base + joints)
        # We need to set the joint positions correctly
        
        # Set floating base position (first 7 DOF: x, y, z, qw, qx, qy, qz)
        if model.nq > motion_data['dof_positions'].shape[1]:
            # Keep floating base at origin for now
            data.qpos[:7] = [0, 0, 0.8, 1, 0, 0, 0]  # x, y, z, qw, qx, qy, qz
            # Set the joint positions
            data.qpos[7:7+motion_data['dof_positions'].shape[1]] = motion_data['dof_positions'][frame]
        else:
            # Direct assignment if dimensions match
            data.qpos[:] = motion_data['dof_positions'][frame]
        
        # Set velocities similarly
        if model.nv > motion_data['dof_velocities'].shape[1]:
            data.qvel[6:6+motion_data['dof_velocities'].shape[1]] = motion_data['dof_velocities'][frame]
        else:
            data.qvel[:] = motion_data['dof_velocities'][frame]
        
        # Forward dynamics
        mujoco.mj_forward(model, data)
        
        # Print progress
        if frame % 100 == 0:
            progress = (frame / len(motion_data['dof_positions'])) * 100
            print(f"Progress: {progress:.1f}% ({frame}/{len(motion_data['dof_positions'])})")
        
        # Next frame
        frame += 1
        
        # Control playback speed
        time.sleep(1.0 / motion_data['fps'][0])
    
    print("Motion playback complete!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python view_g1_motion.py <motion_file>")
        sys.exit(1)
    
    motion_file = sys.argv[1]
    view_g1_motion(motion_file)