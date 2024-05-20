import bpy
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


def align_objects(pants, body, output_pants_file, output_body_file, output_file):
    
    
    
    # Load object files
    bpy.ops.wm.obj_import(filepath=body)
    bpy.ops.wm.obj_import(filepath=pants)
    print('imported')

    # Get all imported objects
    imported_objects = bpy.context.selected_objects

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        print(obj.name)
        obj.select_set(True)

    # Select the first object (assuming it's the active object)
    body_obj = mesh_objects[1]

    # Select the second object
    pants_obj = mesh_objects[2]

    body_obj.rotation_euler = (radians(0), 0 , radians(45))

    bpy.ops.object.select_all(action='DESELECT')
    body_obj = mesh_objects[1]
    body_obj.select_set(True)
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    body_origin_location = body_obj.location
    # print(body_origin_location)
    # Select the second object
    bpy.ops.object.select_all(action='DESELECT')
    pants_obj = mesh_objects[2]
    pants_obj.select_set(True)  
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    bpy.ops.wm.obj_export(filepath=output_file)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    print(f"Initial body location: {body_obj.location}")
    print(f"Initial pants location: {pants_obj.location}")
    ###############################################################################
    bpy.ops.object.select_all(action='DESELECT')
    body_obj = mesh_objects[1]
    body_obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
    body_origin_location_COV = body_obj.location
    print(f"body location cov: {body_origin_location_COV}")

    body_obj.location = (0,0,0)
    print(f"body location reset: {body_obj.location}")
    ###############################################################################
    bpy.ops.object.select_all(action='DESELECT')
    pants_max_y = max([v.co.y for v in pants_obj.data.vertices])
    translation_vector_y = (0,abs(body_origin_location_COV.y-pants_max_y) , 0)
    vector_epsilon = mathutils.Vector((0, 0.07, 0))
    translation_vector_y= mathutils.Vector(translation_vector_y) - vector_epsilon
    for vert in pants_obj.data.vertices:
        vert.co -= translation_vector_y
    ###############################################################################
    # body_min_z = min([v.co.z for v in body_obj.data.vertices])
    # pants_min_z = min([v.co.z for v in pants_obj.data.vertices])

    # print(pants_min_z)
    # print(body_min_z)
    # translation_vector_z = (0, 0, (abs(pants_min_z) - abs(body_min_z)))
    # print(translation_vector_z)
    # translation_vector_z = mathutils.Vector(translation_vector_z)
    # for vert in pants_obj.data.vertices:
    #     vert.co += translation_vector_z

    # pants_min_z_post = min([v.co.z for v in pants_obj.data.vertices])
    # print(pants_min_z_post)

    # print(f"Body location after Z: {body_obj.location}")
    # print(f"Pants location after Z: {pants_obj.location}")
    ############################################################################
    bpy.ops.wm.obj_export(filepath=output_file)
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    rotation_angles = (radians(0), radians(45), radians(0))  # Specify desired rotation (X, Y, Z)
    rotation_quaternion = mathutils.Euler(rotation_angles).to_quaternion()

    

    # Select the pants object
    pants_obj = mesh_objects[2]
    
    bpy.context.view_layer.objects.active = pants_obj
    pants_obj.select_set(True)
    # print('Pants',pants_obj)
    print('Pants',pants_obj.data.vertices)
    pants_vertices=[v.co for v in pants_obj.data.vertices]
    pants_faces=[f.vertices for f in pants_obj.data.polygons]

    #mesh = trimesh.Trimesh(vertices=pants_vertices, faces=pants_faces)
    # Export the pants object
    #mesh.export(output_pants_file)
    mesh_objects2 = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects2:
        print(F"FROM ALIGN PANTS: {obj.name}")
    #pants_obj.rotation_quaternion = rotation_quaternion
    write_obj_file(pants_obj, output_pants_file)
    #export_mesh.save(bpy.context, filepath=output_file, check_existing=False, axis_forward='-Z', axis_up='Y')
    # Export the pants object
    #bpy.ops.export_scene.obj(filepath=output_pants_file, use_selection=True, global_scale=1)

    # Deselect the pants object
    pants_obj.select_set(False)

    bpy.ops.object.select_all(action='DESELECT')

    # Select the nbody object
    nbody_obj = mesh_objects[1]
    bpy.context.view_layer.objects.active = nbody_obj
    nbody_obj.select_set(True)

    # Export the nbody object
    nbody_obj_vertices=[v.co for v in nbody_obj.data.vertices]
    nbody_obj_faces=[f.vertices for f in nbody_obj.data.polygons]
    #mesh = trimesh.Trimesh(vertices=nbody_obj_vertices, faces=nbody_obj_faces)
    #mesh.export(output_body_file)
    #body_obj.rotation_quaternion = rotation_quaternion
    write_obj_file(nbody_obj, output_body_file)


    # Deselect the nbody object
    nbody_obj.select_set(False)
    

import sys
garment_path = sys.argv[5]
body_path = sys.argv[6]
output_pants_file = sys.argv[7]
output_body_file = sys.argv[8]
output_file = sys.argv[9]


# Align objects
align_objects(garment_path, body_path, output_pants_file, output_body_file, output_file)