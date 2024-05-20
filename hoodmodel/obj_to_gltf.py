import aspose.threed as a3d
# Example usage
# obj_file_path = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/obj_00001.obj"
# gltf_file_path = "output234.gltf"

#obj_to_gltf(obj_file_path, gltf_file_path)
def obj_to_gltf(obj_file_path, gltf_file_path):
    scene = a3d.Scene.from_file(obj_file_path)
    scene.save(gltf_file_path)
    return gltf_file_path

import sys

obj_file_path = sys.argv[2]
gltf_file_path = sys.argv[3]

obj_to_gltf(obj_file_path, gltf_file_path)