import bpy

print("Available armature objects in the current Blender file:")
print("=" * 50)

armature_count = 0
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature_count += 1
        print(f"{armature_count}. {obj.name}")
        print(f"   - Location: {obj.location}")
        print(f"   - Visible: {obj.visible_get()}")
        print(f"   - Active: {obj == bpy.context.active_object}")
        print()

if armature_count == 0:
    print("No armature objects found in this file.")
else:
    print(f"Total armatures found: {armature_count}")
