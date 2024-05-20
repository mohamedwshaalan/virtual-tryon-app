import bpy
import os
import mathutils
from math import radians
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
# def locate_objects(path_to_first_obj, path_to_second_obj):
   
#     bpy.ops.wm.obj_import(filepath=path_to_first_obj)
#     object1 = bpy.context.selected_objects
#     bpy.ops.wm.obj_import(filepath=path_to_second_obj)
#     # Get references to the imported objects
    
#     object2 = bpy.context.selected_objects
#     print(object1)
#     # Set the location of object2 to match the location of object1
#     object2[0].location = object1[0].location
#     print(object2[0].location)
#     print(object1[0].location)
#     bpy.ops.wm.obj_export(filepath='newest.obj')
def locate_objects(path_to_first_obj, path_to_second_obj, path_to_third_obj, path_to_fourth_obj, output_file, output_body, output_pants, output_tshirt):
    bpy.ops.wm.obj_import(filepath=path_to_first_obj)
    bpy.ops.wm.obj_import(filepath=path_to_second_obj)
    bpy.ops.wm.obj_import(filepath=path_to_third_obj)
    bpy.ops.wm.obj_import(filepath=path_to_fourth_obj)

        # Get all imported objects
    imported_objects = bpy.context.selected_objects

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        print(obj.name)
        obj.select_set(True)

    object1 = mesh_objects[1]

        # Select the second object
    object2 = mesh_objects[2]

    object3 = mesh_objects[3]

    object4 = mesh_objects[4]

    object2_max_z = max([v.co.z for v in object2.data.vertices])
    object1_max_z = max([v.co.z for v in object1.data.vertices])

    object2_max_y = max([v.co.y for v in object2.data.vertices])
    object1_max_y = max([v.co.y for v in object1.data.vertices])
        # Set the location of object2 to match the location of object1
        #object2.location = object1.location
    bpy.ops.object.select_all(action='DESELECT')
    translation_vector_y = (0, abs(object1_max_y-object2_max_y),abs(object1_max_z-object2_max_z))
    translation_vector_y= mathutils.Vector(translation_vector_y)
    for vert in object2.data.vertices:
        vert.co += translation_vector_y



    translation_pants = (0,abs(object1_max_y-object2_max_y),abs(object1_max_z-object2_max_z))
    translation_pants = mathutils.Vector(translation_pants)
    for vert in object3.data.vertices:
        vert.co += translation_pants

    #-0.01

    translation_tshirts = (0,abs(object1_max_y-object2_max_y)-0.014,0)
    translation_tshirts = mathutils.Vector(translation_tshirts)
    for vert in object4.data.vertices:
        vert.co += translation_tshirts


        # Delete the first object
    bpy.data.objects.remove(mesh_objects[0])
    bpy.data.objects.remove(object1)
        # Export the modified object
    bpy.ops.wm.obj_export(filepath=output_file)
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    i=0
    for obj in mesh_objects:
        if i==0:
            write_obj_file(obj, output_body)
        elif i==1:
            write_obj_file(obj, output_pants)
        elif i==2:
            write_obj_file(obj, output_tshirt)
        
        i+=1

    # bpy.ops.wm.obj_import(filepath=path_to_first_obj)
    # bpy.ops.wm.obj_import(filepath=path_to_second_obj)

    #     # Get all imported objects
    # imported_objects = bpy.context.selected_objects

    # mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    # for obj in mesh_objects:
    #     print(obj.name)
    #     obj.select_set(True)
    
    # object1 = mesh_objects[1]

    #     # Select the second object
    # object2 = mesh_objects[2]

    # object2_max_z = max([v.co.z for v in object2.data.vertices])
    # object1_max_z = max([v.co.z for v in object1.data.vertices])

    # object2_max_y = max([v.co.y for v in object2.data.vertices])
    # object1_max_y = max([v.co.y for v in object1.data.vertices])
    #     # Set the location of object2 to match the location of object1
    #     #object2.location = object1.location
    # bpy.ops.object.select_all(action='DESELECT')
    # translation_vector_y = (0,abs(object1_max_y-object2_max_y),abs(object1_max_z-object2_max_z))
    # translation_vector_y= mathutils.Vector(translation_vector_y)
    # for vert in object2.data.vertices:
    #     vert.co += translation_vector_y

    # bpy.data.objects.remove(mesh_objects[0], do_unlink=True)
    #     # Delete the first object
    # bpy.data.objects.remove(object1, do_unlink=True)
    # #delete the cube
    
    

    #     # Export the modified object
    # bpy.ops.wm.obj_export(filepath='final_body.obj')
import sys

path_to_first_obj = sys.argv[5]
path_to_second_obj = sys.argv[6]
path_to_third_obj = sys.argv[7]
path_to_fourth_obj = sys.argv[8]
output_file = sys.argv[9]
output_body = sys.argv[10]
output_pants = sys.argv[11]
output_tshirt = sys.argv[12]

# path_to_first_obj = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/obj_00001.obj'
# path_to_second_obj = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/fit_body.obj'
# path_to_third_obj = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/pants_tex.obj'
# path_to_fourth_obj = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/tshirt_tex.obj'
# output_file = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/tryyy.obj'
# output_body = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/out_body.obj'
# output_pants = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/out_pants.obj'
# output_tshirt = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/out_tshirt.obj'

# path_to_first_obj = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/obj_00001.obj'
# path_to_second_obj = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/merged_output.obj'
locate_objects(path_to_first_obj, path_to_second_obj, path_to_third_obj, path_to_fourth_obj, output_file, output_body, output_pants, output_tshirt)