import bpy

def merge_objects(objfile1, objfile2, outputFilePath):
    # Clear existing objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Import first OBJ file
    bpy.ops.wm.obj_import(filepath=objfile1)
    
    
    obj1 = bpy.context.selected_objects[0]

    # Import second OBJ file
    bpy.ops.wm.obj_import(filepath=objfile2)
    #bpy.ops.import_scene.obj(filepath=objfile2)
    obj2 = bpy.context.selected_objects[0]

    # # Move objects to center
    # obj1.location = (0, 0, 0)
    # obj2.location = (1, 0, 0)

    # Join objects
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    obj2.select_set(True)
    bpy.ops.object.join()

    # Remove doubles (merge vertices by distance)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')
    #reset rotation
    # bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    # bpy.context.object.rotation_euler = (0, 0, 0)
    # Export the merged object as .obj file
    mergedObject = bpy.context.selected_objects[0]

    bpy.ops.wm.obj_export(filepath=outputFilePath)

    #bpy.ops.export_scene.obj(filepath=outputFilePath, use_selection=True)

    # Print a message
    print("Merged objects successfully.")

import sys
garment_path = sys.argv[5]
body_path = sys.argv[6]
output_file = sys.argv[7]

merge_objects(body_path, garment_path, output_file)

