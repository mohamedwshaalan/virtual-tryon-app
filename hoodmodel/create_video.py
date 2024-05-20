import bpy
import mathutils
from math import radians
from mathutils import Vector
import numpy as np
def create_video(obj_filepath ):
    # Path to your OBJ file
    
    # Import OBJ file with custom options to preserve texture paths
    bpy.ops.wm.obj_import(filepath=obj_filepath)
    #bpy.ops.import_scene.obj(filepath=obj_filepath, use_image_search=False)
    # Set up world
    # bpy.context.scene.world.use_nodes = True
    # world = bpy.context.scene.world
    # bg_node = world.node_tree.nodes['Background']
    # bg_node.inputs[0].default_value = (0.2, 0.4, 0.6, 1)  # Set background color (RGBA)

    # Get the imported mesh object
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        print(obj.name)
    if mesh_objects:
        mesh_object = mesh_objects[0]
    else:
        raise ValueError("No mesh object found in the scene after importing OBJ file.")
    mesh_objects[1].select_set(True)
    mesh_objects[1].rotation_euler = (radians(0), 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    mesh_objects[2].select_set(True)
    mesh_objects[2].rotation_euler = (radians(0), 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    mesh_objects[3].select_set(True)
    mesh_objects[3].rotation_euler = (radians(0), 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    #Remove the unused mesh object
    bpy.data.objects.remove(mesh_object, do_unlink=True)
    camera = bpy.data.objects['Camera'] if 'Camera' in bpy.data.objects else None
    if not camera:
        bpy.ops.object.camera_add()
        camera = bpy.context.object

    

    # Position the camera closer to the object for a zoomed-in effect
    camera.location = (0, -5, 0)  # Adjust these values as needed for your specific zoom level and object size
    camera.rotation_euler = (radians(90), 0, 0)  # Point the camera at the object
    bpy.ops.object.select_all(action='DESELECT')

    #remove old lighting
    lighting = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
    lighting[0].select_set(True)
    # bpy.ops.object.delete()
    
    # # Create a new light source
    # bpy.ops.object.light_add(type='AREA')
    # light_ob = bpy.context.object
    # light_ob.location = (0.000817,-1.03,-1.54438)
    # light_ob.rotation_euler = (radians(151.873), radians(-19.1547), radians(-31.5426))
    # light = light_ob.data
    lighting[0].data.energy = 2500
    #light.color = (1, 1, 1)

    # Set active object
    # bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

    # Set rotation to (0, 0, 0)
    #bpy.context.object.rotation_euler = (0, 0, 0)

    # Set output video format

    # Set up rotation for each mesh object
    rotation_degrees_per_frame = 360  # Rotate 360 degrees per frame
    frame_end = 100  # Total frames
    rotation_step = rotation_degrees_per_frame / frame_end

    

    # Set rotation keyframes for each mesh object
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        obj.select_set(True)
        obj.rotation_euler = (radians(0), 0, 0)  # Start rotation

        for frame in range(frame_end + 1):
            bpy.context.scene.frame_set(frame)
            obj.rotation_euler = (0, 0, radians(frame * rotation_step))  # Rotate over frames

            # Insert keyframe for rotation
            obj.keyframe_insert(data_path="rotation_euler", index=-1)

        obj.select_set(False)


    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'

    # Set output file path
    output_filepath = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/final_video.mp4'
    bpy.context.scene.render.filepath = output_filepath

    # Set resolution
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # Set up frame range
    frame_start = 1
    frame_end = 100
    frame_step = 1
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    bpy.context.scene.frame_step = frame_step

    # Render animation
    bpy.ops.render.render(animation=True)


import sys
obj_filepath = sys.argv[5]
create_video(obj_filepath)