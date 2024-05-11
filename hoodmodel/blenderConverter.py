import bpy


def convert():
    # Wipe Scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import .obj
    files = [{"name": "blenderObj.obj"}]
    bpy.ops.wm.obj_import(files=files)

    # Rotate and Scale .obj
    obj = bpy.context.selected_objects[0]
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (5, 5, 5)

    # Add new Material to .obj
    bpy.ops.material.new()
    material = bpy.data.materials[-1]
    obj.data.materials.append(material)

    # Configure Material
    node_tree = material.node_tree
    bsdf = node_tree.nodes[0]
    color_attribute = node_tree.nodes.new(type="ShaderNodeVertexColor")
    color_attribute.layer_name = "Color"
    node_tree.links.new(color_attribute.outputs["Color"], bsdf.inputs["Base Color"])

    # Configure Bake
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_direct = False
    scene.cycles.bake_type = 'DIFFUSE'
    scene.render.bake.margin = 5

    # Prepare image
    image_texture = node_tree.nodes.new(type="ShaderNodeTexImage")
    image = bpy.data.images.new('bake', 1024, 1024)
    image_texture.image = image

    # Create UV Map
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.002)
    bpy.ops.object.editmode_toggle()

    # Bake
    node_tree.nodes.active = image_texture
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')

    # Save image
    image.filepath_raw = '//dispatch//bake.png'
    image.file_format = "PNG"
    image.save()

    # Save .obj
    bpy.ops.export_scene.obj(filepath='dispatch/object.obj', use_materials=False)