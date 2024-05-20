import bpy

# # Get all imported objects
# cloth2tex_tshirt_path = '/home/mahdy/Desktop/HOOD_Model/hood_data/fromanypose/aligned_tshirt.obj'
# hood_tshirt_path = '/home/mahdy/Desktop/automatic_export tshirt/obj_00000.obj'
# output_tshirt_file='/home/mahdy/Desktop/objects_with_texture/hood_copied_uv_w_texture.obj'
# image_path = "/home/mahdy/Downloads/0_texture_uv_1000(1).jpg"  # Update with your image file path

def apply_texture(cloth2tex_tshirt_path,hood_tshirt_path,output_tshirt_file,image_path):
    
    bpy.ops.wm.obj_import(filepath=cloth2tex_tshirt_path)
    bpy.ops.wm.obj_import(filepath=hood_tshirt_path)

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in mesh_objects:
        obj.select_set(True)
        print(obj.name)
    cube_obj = mesh_objects[0]
    cloth2tex_tshirt = mesh_objects[1]
    hood_tshirt = mesh_objects[2]
    # Clear all existing materials from the tshirt_obj
    cloth2tex_tshirt.data.materials.clear()
    hood_tshirt.data.materials.clear()
    bpy.data.objects.remove(cube_obj)

    bpy.ops.object.select_all(action='DESELECT')

    if hood_tshirt and cloth2tex_tshirt:
        print("Bye")
        hood_tshirt.select_set(True)
        cloth2tex_tshirt.select_set(True)

    hood_tshirt.select_set(True)
    cloth2tex_tshirt.select_set(True)

    # Ensure both objects have mesh data
    if cloth2tex_tshirt.type != 'MESH' or hood_tshirt.type != 'MESH':
        print("Both source and target objects must be meshes.")
        quit()

    # Ensure both objects have UV data
    if not cloth2tex_tshirt.data.uv_layers:
        print("Source object doesn't have UV data.")
        quit()

    # Check if the target object already has UV data, if not create a new UV layer
    if not hood_tshirt.data.uv_layers:
        hood_tshirt.data.uv_layers.new(name="UVMap")

    # Access UV data of the source object
    source_uv_layer = cloth2tex_tshirt.data.uv_layers.active.data

    # Access UV data of the target object
    target_uv_layer = hood_tshirt.data.uv_layers.active.data

    # Copy UV data from source to target
    print(len(hood_tshirt.data.polygons))
    # for poly in hood_tshirt.data.polygons:
    #     #print(len(poly.loop_indices))
    #     for loop_index in poly.loop_indices:
    #         #print(loop_index)
    #         print(len(poly.loop_indices))
    #         for i in range(0, len(poly.loop_indices)):
    #             source_loop_index = poly.loop_indices[i]
    #             source_uv = source_uv_layer[source_loop_index].uv
    #             target_uv_layer[loop_index].uv = source_uv
    # Iterate over polygons of the target object
    for target_poly, source_poly in zip(hood_tshirt.data.polygons, cloth2tex_tshirt.data.polygons):
        # Ensure the source polygon has enough loops
        if len(source_poly.loop_indices) < len(target_poly.loop_indices):
            print("Source object doesn't have enough loops to copy UVs.")
            break
        # Iterate over loop indices of the target polygon
        for i, target_loop_index in enumerate(target_poly.loop_indices):
            # Calculate the corresponding source loop index using modulo to ensure it wraps around
            source_loop_index = source_poly.loop_indices[i % len(source_poly.loop_indices)]
            # Copy UV coordinate from source to target
            target_uv_layer[target_loop_index].uv = source_uv_layer[source_loop_index].uv


    # Load the image

    image = bpy.data.images.load(image_path)


    # Create a new material
    material = bpy.data.materials.new(name="TextureMaterial")
    material.use_nodes = True
    tree = material.node_tree

    # Clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    # Create texture node
    texture_node = tree.nodes.new('ShaderNodeTexImage')
    texture_node.image = image

    # Create principled BSDF node
    principled_bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')

    # Create output node
    output_node = tree.nodes.new('ShaderNodeOutputMaterial')

    # Link nodes
    tree.links.new(texture_node.outputs['Color'], principled_bsdf.inputs['Base Color'])
    tree.links.new(principled_bsdf.outputs['BSDF'], output_node.inputs['Surface'])

    # Apply the material to the mesh
    hood_tshirt.data.materials.append(material)
    bpy.data.objects.remove(cloth2tex_tshirt)
    bpy.ops.wm.obj_export(filepath=output_tshirt_file) #Not needed for app, just for testing
    print("UV data copied from source to target object.")


import sys
cloth2tex_tshirt_path=sys.argv[5]
hood_tshirt_path=sys.argv[6]
output_tshirt_file=sys.argv[7]
image_path=sys.argv[8]



apply_texture(cloth2tex_tshirt_path,hood_tshirt_path,output_tshirt_file,image_path)
