# MikuMotionTools

MikuMotionTools contains various functions for converting MMD (MikuMikuDance) motions and other motion file formats into armature motion format that can be used in the Isaac Lab RL training environment.


## Getting Started

### Create the environment

```bash
uv sync
```

To run the examples, do

```bash
uv sync --extra examples
```

### Install the library

From pip (coming soon)

```bash
uv pip install mikumotion
```

From source
```bash
git clone https://github.com/T-K-233/MikuMotionTools.git
cd ./MikuMotionTools/
uv pip install -e .
```


## Running examples

Export motion from Blender.

This script only exports the body pose data. The joint data will be empty, and need to be filled in with the following retargeting script.

```bash
blender ./blender-projects/G1_Zamuza.blend --python ./scripts/examples/extract_g1_zamuza.py
```

View motion with matplotlib:

```bash
uv run ./scripts/view_motion.py --motion ./data/motions/g1_zamuza_0_1632.npz
```

Run retargeting logic to solve for joint data.

```bash
uv run ./scripts/examples/retarget_g1.py --motion ./data/motions/g1_zamuza_0_1632.npz --robot unitree_g1 --realtime
```


## Directory Structure

`blender-projects/` stores the blender project files. 

`mikumotion/` stores the Python source file of the library.

`data/motions/` stores the converted motions.

`data/robots/` stores the robot asset file used during inverse kinematic solving.

Note: Due to licensing issue, the Blender project files and MMD motions should be retrieved from the original authors. For internal developers, the mirror of this directory is stored at [Google Drive](https://drive.google.com/drive/folders/1sFQmo_UvkY5xSIZKLjXLxlAOpLdI_1jz?usp=drive_link).


## Motion Format

This library uses the motion file format defined in IsaacLab [MotionLoader](https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab_tasks/isaaclab_tasks/direct/humanoid_amp/motions/motion_loader.py#L12).

Each motion file is a numpy dictionary with the following fields. Here, we assume the robot has `D` number of joints and `B` number of linkages, and the motion file has `F` frames.

- `fps`: an int64 number representing the frame rate of the motion data.
- `dof_names`: a list of length `D` containing the names of each joint.
- `body_names`: a list of length `B` containing the names of each link.
- `dof_positions`: a numpy array of shape `(F, D)` containing the rotational positions of the joints in `rad`.
- `dof_velocities`: a numpy array of shape `(F, D)` containing the rotational (angular) velocities of the joints in `rad/s`.
- `body_positions`: a numpy array of shape `(F, B, 3)` containing the locations of each body in **world frame**, in `m`.
- `body_rotations`: a numpy array of shape `(F, B, 4)` containing the rotations of each body in **world frame**, in quaternion `(qw, qx, qy, qz)`.
- `body_linear_velocities`: a numpy array of shape `(F, B, 3)` containing the linear velocities of each body in **world frame**, in `m/s`.
- `body_angular_velocities`: a numpy array of shape `(F, B, 3)` containing the rotational (angular) velocities of each body in **world frame**, in `rad/s`.

The converted motion file is targeted for one particular robot skeleton structure. 

To ensure best performance, also make sure that the frame rate matches the training environment policy update rate to avoid expensive interpolations.

### Generic Joint Names

We follow the [SMPL-X joint name](https://github.com/vchoutas/smplx/blob/main/smplx/joint_names.py#L244C21-L268C18) as a generic joint naming convention.

```
    "pelvis",
    "left_hip",
    "right_hip",
    "spine1",
    "left_knee",
    "right_knee",
    "spine2",
    "left_ankle",
    "right_ankle",
    "spine3",
    "left_foot",
    "right_foot",
    "neck",
    "left_collar",
    "right_collar",
    "head",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hand",
    "right_hand",
```


## Working with MMD

To import and convert MMD motions in Blender, the [MMD Tools](https://extensions.blender.org/add-ons/mmd-tools/) plugin needs to be installed to Blender.


## Motion data
View the retargeted motion
 ```  
 uv run ./scripts/view_motion.py --motion ./data/motions/g1_zamuza_0_1632_retargeted.npz
 ```
Compare with the original:
```   
uv run ./scripts/view_motion.py --motion ./data/motions/g1_zamuza_0_1632.npz
```

   MikuMotionTools Workflow

1. Motion Data Import
You have motion data (like g1_zamuza_0_1632.npz) that contains human/character movement information
This data includes body positions, rotations, and velocities for each frame

2. Blender Processing (Optional - for new motion extraction)
Blender loads a 3D model with an armature (skeleton)
The extract_g1_zamuza.py script runs through each frame of animation
It extracts bone positions, rotations, and velocities from the 3D model
This creates the motion data file (.npz format)

3. Motion Retargeting (What we just did)
The retarget_g1.py script takes the human motion data
It loads the Unitree G1 robot model (from the MJCF XML file)
It maps human body parts to robot joints using a mapping table:
left_rubber_hand → robot hand joint
left_ankle_roll_link → robot foot joint
pelvis → robot base joint
etc.

4. Inverse Kinematics Solving
For each frame, the script uses inverse kinematics to find robot joint angles
It tries to make the robot's body parts match the human's body positions
It solves this as an optimization problem with weights and constraints

5. Output
Generates a new motion file (g1_zamuza_0_1632_retargeted.npz)
Contains robot joint positions, velocities, and body data
Ready to use for robot simulation or training
The Key Insight
The "retargeting" is essentially translating human motion into robot motion by:
Mapping human body parts to robot joints
Solving for joint angles that achieve similar poses
Converting the motion from human skeleton to robot skeleton


## How the System Knows About G1 Joints

1. Robot Model Definition
The G1 robot is defined in the MJCF (MuJoCo) XML file at ./data/robots/unitree/g1/mjcf/g1_29dof_mode_5_mocap.xml. This file contains:
29 degrees of freedom (joints) - hence "29dof" in the filename
Complete joint hierarchy with names like left_hip_pitch_joint, right_elbow_joint, etc.
Physical properties (mass, inertia, joint limits, etc.)

2. Joint Structure
The G1 has a 29-DOF humanoid structure:
Legs: 6 joints each (hip pitch/roll/yaw, knee, ankle pitch/roll)
Arms: 7 joints each (shoulder pitch/roll/yaw, elbow, wrist roll/pitch/yaw)
Torso: 3 joints (waist yaw/roll/pitch)

3. Blender vs G1 Joint Mapping
They DON'T match directly! Here's the key insight:
Blender motion data has body names like left_rubber_hand, left_ankle_roll_link
G1 robot model has joint names like left_elbow_joint, left_ankle_roll_joint
The mapping table in retarget_g1.py bridges this gap

Blender joints ≠ G1 joints - they're completely different structures
Blender provides targets (where body parts should be)
G1 provides the mechanism (how to get there with 29 joints)
IK solver bridges the gap by finding joint angles that achieve the target poses

## Mapping
pelvis → pelvis (highest priority: pos_weight=10.0)
left_rubber_hand → left_rubber_hand (hand position)
right_rubber_hand → right_rubber_hand (hand position)
left_ankle_roll_link → left_ankle_roll_link (foot position)
right_ankle_roll_link → right_ankle_roll_link (foot position)
left_shoulder_roll_link → left_shoulder_roll_link (shoulder position)
left_elbow_link → left_elbow_link (elbow position)
right_shoulder_roll_link → right_shoulder_roll_link (shoulder position)
right_elbow_link → right_elbow_link (elbow position)
left_hip_roll_link → left_hip_roll_link (hip position)
right_hip_roll_link → right_hip_roll_link (hip position)
left_knee_link → left_knee_link (knee position)
right_knee_link → right_knee_link (knee position)

## Priority System:
Pelvis has the highest weight (10.0) - it's the most important reference point
Hands and feet have moderate weights (1.0) for position and orientation
Joints (shoulders, elbows, hips, knees) have position weight (1.0) but no orientation weight (0.0)

## Why Some Aren't Mapped:
torso_link: Redundant with pelvis (pelvis already controls torso movement)
head_link: G1 robot doesn't have a head joint, so it can't be controlled

The IK solver uses these 13 target positions to find the 29 joint angles that make the G1 robot's body parts reach those positions. 

### The main pipeline is: Extract → Retarget → View

1. 3D Character in Blender
   ↓ (extract_g1_zamuza.py)
2. Human Motion Data (.npz)
   ↓ (retarget_g1.py)
3. Robot Motion Data (.npz)
   ↓ (view_motion.py)
4. 3D Visualization

1. extract_g1_zamuza.py - Motion Extraction from Blender
Purpose: Extracts motion data from a 3D character in Blender
What it does:
Runs inside Blender with a 3D character model
Goes through each frame of animation (0-600 frames)
Extracts bone positions, rotations, and velocities
Saves motion data as .npz file
Input: Blender project file (G1_Zamuza.blend)
Output: Motion file (g1_zamuza_0_600_body_only.npz)

2. retarget_g1.py - Motion Retargeting to Robot
Purpose: Converts human motion to robot motion
What it does:
Loads human motion data
Loads G1 robot model (29 joints)
Maps human body parts to robot joints
Uses inverse kinematics to solve for joint angles
Saves retargeted motion
Input: Human motion file + robot model
Output: Robot motion file (g1_zamuza_0_1632_retargeted.npz)

3. view_motion.py - Motion Visualization
Purpose: Visualizes motion data
What it does:
Loads motion files (human or robot)
Creates 3D plots showing body movement
Shows key body parts (hands, feet, pelvis)
Can render full scene or simplified view
Input: Any motion file (.npz)
Output: Interactive 3D visualization

## DeepWiki
https://deepwiki.com/T-K-233/MikuMotionTools
