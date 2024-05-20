import bpy
import os
import mathutils
from math import radians
# Set paths to your object files
# body = "/home/mahdy/Desktop/pants&body/body_examples/tall.obj"#input 1
# tshirt = "/home/mahdy/Desktop/resized_garments/T-shirt/medium_tall.obj"#input 2
# output_file = "/home/mahdy/Desktop/pants&body/original_body_tshirt.obj"
# output_body_rotated = "/home/mahdy/Desktop/pants&body/rotated_body.obj" #Temporary output file in backend
# output_body_file = "/home/mahdy/Desktop/pants&body/output_aligned_body_for_pants.obj" ######################3 you need this as the output 
# output_tshirt_file = "/home/mahdy/Desktop/pants&body/output_aligned_pants.obj"############################3you also need this as the output
def write_obj_file(mesh_obj, output_file):
    mesh_data = mesh_obj.data
    object_matrix_world = mesh_obj.matrix_world

    # Open the output OBJ file
    with open(output_file, 'w') as f:
        # Write vertex coordinates
        for vertex in mesh_data.vertices:
            # Apply object's transformation matrix to vertex coordinates
            world_co = object_matrix_world @ vertex.co
            f.write(f"v {world_co.x} {world_co.y} {world_co.z}\n")

        # Write vertex normals
        for vertex in mesh_data.vertices:
            normal = vertex.normal
            f.write(f"vn {normal.x} {normal.y} {normal.z}\n")

        # Write texture coordinates
        if mesh_data.uv_layers.active:
            uv_layer = mesh_data.uv_layers.active.data
            for uv_data in uv_layer:
                uv = uv_data.uv
                f.write(f"vt {uv.x} {uv.y}\n")

        # Write faces
        for face in mesh_data.polygons:
            f.write("f ")
            for loop_index in face.loop_indices:
                vertex_index = mesh_data.loops[loop_index].vertex_index + 1
                uv_index = face.loop_indices.index(loop_index) + 1 if mesh_data.uv_layers.active else None
                normal_index = mesh_data.loops[loop_index].vertex_index + 1
                if uv_index is not None:
                    f.write(f"{vertex_index}/{uv_index}/{normal_index} ")
                else:
                    f.write(f"{vertex_index}//{normal_index} ")
            f.write("\n")
def align_objects(shirts, body, output_shirts_file, output_body_file, output_file):
    # Load object files
    bpy.ops.wm.obj_import(filepath=body)

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        # print(obj.name)
        obj.select_set(True)
    # are you done?
    #it's training, you can use it until it finishes
    #I need the GPU
    #i need a few more momentssssssss
    #wait a few minutes, it isn't gonna take long
    # Select the first object (assuming it's the active object)
    body_obj = mesh_objects[1]
    body_obj.rotation_euler = (radians(0), 0 , radians(0))
    output_body_rotated = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/rotated_body.obj" #Temporary output file in backend
    bpy.ops.wm.obj_export(filepath=output_body_rotated)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in mesh_objects:
        bpy.data.objects.remove(obj)

    bpy.ops.wm.obj_import(filepath=output_body_rotated)
    bpy.ops.wm.obj_import(filepath=shirts)

    # Get all imported objects
    imported_objects = bpy.context.selected_objects

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        # print(obj.name)
        obj.select_set(True)

    # Select the first object (assuming it's the active object)
    body_obj = mesh_objects[1]
    print(body_obj.name)
    # Select the second object
    tshirt_obj = mesh_objects[2]
    print(tshirt_obj.name)

    body_verts = [(v.co.x, v.co.y, v.co.z) for v in body_obj.data.vertices]

    body_max_x = max([v.co.x for v in body_obj.data.vertices])
    body_max_y = max([v.co.y for v in body_obj.data.vertices])
    body_min_y = min([v.co.y for v in body_obj.data.vertices])

    bpy.ops.object.select_all(action='DESELECT')
    body_obj = mesh_objects[1]
    body_obj.select_set(True)
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    body_origin_location = body_obj.location

    bpy.ops.object.select_all(action='DESELECT')
    tshirt_obj = mesh_objects[2]
    tshirt_obj.select_set(True)  
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')


    body_obj.location = (0,0,0)
    tshirt_obj.location = (0,0,0)
    ##############################################################################
    bpy.ops.object.select_all(action='DESELECT')
    body_obj = mesh_objects[1]
    body_obj.select_set(True)

    bpy.ops.object.select_all(action='DESELECT')
    tshirt_obj = mesh_objects[2]
    tshirt_obj.select_set(True)  

    body_verts = [(v.co.x, v.co.y, v.co.z) for v in body_obj.data.vertices]
    body_max_x = max([v.co.x for v in body_obj.data.vertices])
    body_max_y = max([v.co.y for v in body_obj.data.vertices])
    body_min_y = min([v.co.y for v in body_obj.data.vertices])
    tshirt_max_y = max([v.co.y for v in tshirt_obj.data.vertices])

    height = body_max_y-body_min_y
    print(height)
    height_ratio = height/(12.085600197315216*2.0)
    print(f"Ratio:{height_ratio}")
    # bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
    body_origin_location = body_obj.location
    print(body_origin_location)
    print(tshirt_obj.location)
    y_of_max_x = 0
    for vertex in body_verts:
        if vertex[0]==body_max_x:
            # Update the maximum x-coordinate and its corresponding y-coordinate
            y_of_max_x = vertex[1]

    desired_y = y_of_max_x
    shirt_min_y = min([v.co.y for v in tshirt_obj.data.vertices])
    translation_vector_y = (0, abs(body_max_y  - tshirt_max_y), 0)

    translation_vector_y = mathutils.Vector(translation_vector_y)
    vector_epsilon = mathutils.Vector((0, -0.27 , 0))
    for vert in tshirt_obj.data.vertices:
        vert.co += (translation_vector_y+vector_epsilon)

    bpy.ops.object.select_all(action='DESELECT')
    body_obj = mesh_objects[1]
    body_obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
    body_origin_location = body_obj.location
    # print(body_origin_location)
    # Select the second object
    bpy.ops.object.select_all(action='DESELECT')
    tshirt_obj = mesh_objects[2]
    tshirt_obj.select_set(True)  
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
    tshirt_origin_location = tshirt_obj.location

    translation_vector_x= (abs(body_origin_location.x - tshirt_origin_location.x), 0, 0)
    translation_vector_x = mathutils.Vector(translation_vector_x)
    # for vert in tshirt_obj.data.vertices:
    #     vert.co += (translation_vector_x)

    #body_obj.location = (0,0,0)
    # print(f"Initial body location: {body_obj.location}")
    # print(f"Initial pants location: {tshirt_obj.location}")
    # Export the modified pants object

    bpy.ops.wm.obj_export(filepath=output_file) #Not needed for app, just for testing

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')


    # Select the pants object
    tshirt_obj = mesh_objects[2]
    tshirt_obj.select_set(True)

    
    # Export the pants object
    write_obj_file(tshirt_obj, output_shirts_file)
    #bpy.ops.export_scene.obj(filepath=output_shirts_file, use_selection=True, global_scale=1)

    # Deselect the pants object
    tshirt_obj.select_set(False)

    bpy.ops.object.select_all(action='DESELECT')

    # Select the nbody object
    nbody_obj = mesh_objects[1]
    nbody_obj.select_set(True)
    mesh_objects2 = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects2:
        print(F"FROM ALIGN TSHIRT: {obj.name}")
    write_obj_file(nbody_obj, output_body_file)

    # Export the nbody object
    #bpy.ops.export_scene.obj(filepath=output_body_file, use_selection=True, global_scale=1)

    # Deselect the nbody object
    nbody_obj.select_set(False)
    os.remove(output_body_rotated)

import sys
# shirts='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/garment.obj'
# body='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/merged_output.obj'
# output_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output1.obj'
# output_shirts_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output2.obj'
# output_body_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output3.obj'

shirts = sys.argv[5]
body = sys.argv[6]
output_file = sys.argv[9]
output_shirts_file = sys.argv[7]
output_body_file = sys.argv[8]

# body = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/body.obj"#input 1
# shirts = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/garment.obj"#input 2
# output_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output1.obj'
# output_shirts_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output2.obj'
# output_body_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output3.obj'

# shirts='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/garment.obj'
# body='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/merged_output.obj'
# output_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output12.obj'
# output_shirts_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output22.obj'
# output_body_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/aligned_output32.obj'
align_objects(shirts, body, output_shirts_file, output_body_file, output_file)