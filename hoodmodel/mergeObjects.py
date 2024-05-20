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
    # mergedObject.rotation_euler = (0, 0, 0)  # Adjust rotation as needed
    bpy.ops.wm.obj_export(filepath=outputFilePath)
    #bpy.ops.uv.smart_project(island_margin=0.05)  # Adjust island margin as needed
    # Set up rendering settings
    # bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    # bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    # bpy.context.scene.render.filepath = outputFilePath  # Adjust output file path as needed
    # bpy.context.scene.render.resolution_x = 1920
    # bpy.context.scene.render.resolution_y = 1080

    # # Set up frame range
    # frame_start = 1
    # frame_end = 100
    # frame_step = 1
    # bpy.context.scene.frame_start = frame_start
    # bpy.context.scene.frame_end = frame_end
    # bpy.context.scene.frame_step = frame_step

    # # Render animation
    # bpy.ops.render.render(animation=True)
    

    #bpy.ops.export_scene.obj(filepath=outputFilePath, use_selection=True)

    
    print("Merged objects successfully.")

import sys
garment_path = sys.argv[5]
body_path = sys.argv[6]
output_file = sys.argv[7]
# body_path='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/final_body.obj'
# garment_path='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/tshirt_tex.obj'
# output_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/merged_output222.obj'

merge_objects(body_path, garment_path, output_file)

