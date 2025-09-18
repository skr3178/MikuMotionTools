import bpy

print("=== MMD Model Bone Analysis ===")
print()

armature = bpy.data.objects.get("TdaéÆèââπÉ~ÉNÅEÉAÉyÉìÉh Ver1.10_arm")

if armature and armature.data:
    print(f"Armature: {armature.name}")
    print(f"Armature data: {armature.data.name}")
    print()
    print("All bones in the MMD model:")
    for i, bone in enumerate(armature.data.bones):
        print(f"  {i:3d}: {bone.name}")
    print()
    print(f"Total bones in MMD model: {len(armature.data.bones)}")
    print()
    print("=== Mapping Analysis ===")
    mmd_mapping_bones = ["腰", "足.L", "足.R", "上半身", "ひざ.L", "ひざ.R", "上半身2", "足首.L", "足首.R", "首", "足先EX.L", "足先EX.R", "肩.L", "肩.R", "頭", "腕.L", "腕.R", "ひじ.L", "ひじ.R", "手首.L", "手首.R"]
    print("Bones used in the mapping:")
    found_bones = []
    missing_bones = []
    for bone_name in mmd_mapping_bones:
        if bone_name in armature.data.bones:
            found_bones.append(bone_name)
            print(f"  ✓ {bone_name}")
        else:
            missing_bones.append(bone_name)
            print(f"  ✗ {bone_name} (MISSING)")
    print()
    print(f"Found: {len(found_bones)}/{len(mmd_mapping_bones)} mapping bones")
    print(f"Missing: {len(missing_bones)} mapping bones")
    if missing_bones:
        print("\nMissing bones:")
        for bone in missing_bones:
            print(f"  - {bone}")
    print()
    print("=== Bone Hierarchy ===")
    def print_bone_hierarchy(bone, level=0):
        indent = "  " * level
        print(f"{indent}{bone.name}")
        for child in bone.children:
            print_bone_hierarchy(child, level + 1)
    root_bones = [bone for bone in armature.data.bones if bone.parent is None]
    for root_bone in root_bones:
        print_bone_hierarchy(root_bone)
else:
    print("ERROR: Could not find armature or armature data")
    print("Available objects:")
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            print(f"  - {obj.name} (data: {obj.data is not None})")