import bpy

def merge_objects(objfile1, objfile2, outputFilePath):
    bpy.ops.scene.new(type='NEW')

    bpy.ops.wm.obj_import(filepath=objfile1)
    bpy.ops.wm.obj_import(filepath=objfile2)

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    obj1 = mesh_objects[0]
    obj2 = mesh_objects[1]

    obj1.location = (0, 0, 0)
    obj2.location = (-1, 0, 0)

    obj1.select_set(True)
    obj2.select_set(True)

    bpy.ops.object.join()

    # Remove doubles (merge vertices by distance)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold = 0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Export the merged object as .obj file
    bpy.ops.export_scene.obj(filepath = outputFilePath, use_selection=True)

    # Print a message
    print("Merged objects successfully.")

if(__name__ == "__main__"):
    body = "/home/mahdy/Desktop/pants&body/body.obj"
    shirt = "/home/mahdy/Desktop/pants&body/not_aligned_shirt.obj"

    merge_objects(body, shirt, "mergedObject.obj")

