import bpy
import os

# Set paths to your object files
object_file_1 = "/home/mahdy/Desktop/automatic_export pants/obj_00001.obj"
object_file_2 = "/home/mahdy/Desktop/automatic_export pants/obj_00000.obj"
output_file = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/output_modified9.obj"


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

def delete_verts(object_file_1, object_file_2, output_file,output_file_pants,output_file_body):
    # Load object files
    bpy.ops.wm.obj_import(filepath=object_file_1)
    bpy.ops.wm.obj_import(filepath=object_file_2)


    # Get all imported objects
    imported_objects = bpy.context.selected_objects

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        obj.select_set(True)

    # for obj in mesh_objects:
    #     # print(obj.name)
    #     if obj.name == "Cube":
    #         mesh_objects.remove(obj)

    print(len(mesh_objects))
    # Check if at least two objects are imported
    # if len(mesh_objects) < 2:
    #     print("At least two objects are required for this operation.")
    #     quit()

    # Select the first object (assuming it's the active object)
    obj_1 = mesh_objects[1]

    # Select the second object
    obj_2 = mesh_objects[2]

    # Deselect all objects
    # bpy.ops.object.select_all(action='DESELECT')

    # # Select the first object
    # obj_1.select_set(True)
    # bpy.context.view_layer.objects.active = obj_1

    # # Select the second object
    # obj_2.select_set(True)


    bpy.ops.object.mode_set(mode='OBJECT')

    # Get vertex coordinates of the second object
    obj_2_verts = [(v.co.x, v.co.y, v.co.z) for v in obj_2.data.vertices]
    max_x_co = max([v.co.x for v in obj_2.data.vertices])
    min_x_co = min([v.co.x for v in obj_2.data.vertices])

    # print(obj_2_verts)

    # Go through each vertex of the first object and remove if its coordinates are similar to the second object
    # bpy.ops.mesh.select_all(action='DESELECT')
    for v in obj_1.data.vertices:
        similar_vertex_found = False
        for v2 in obj_2_verts:
            if ((round(v.co.z, 3) == round(v2[2], 3)) and v.co.x < max_x_co and v.co.x > min_x_co):
                #print(f"FOUND {v.co.y} == {v2[1]}")
                v.select = True
        #         break
        # if similar_vertex_found:
        #     v.select = True

    # Delete selected vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')


    # Go back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Export the modified object
    bpy.ops.wm.obj_export(filepath=output_file)
    write_obj_file(obj_1, output_file_body)
    write_obj_file(obj_2, output_file_pants)

    # Clean up (optional)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects.remove(obj_1)
    bpy.data.objects.remove(obj_2)

import sys
object_file_1=sys.argv[5]
object_file_2=sys.argv[6]
output_file=sys.argv[7]
output_file_pants=sys.argv[8]
output_file_body=sys.argv[9]

# object_file_1='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/fit_body.obj'
# object_file_2='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/pants_tex.obj'
# output_file='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/output_modified9.obj'
# output_file_pants='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/output_modified_pants.obj'
# output_file_body='/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/output_modified_body.obj'

delete_verts(object_file_1, object_file_2, output_file,output_file_pants,output_file_body)
