from flask import Flask, request, jsonify, redirect, url_for
import bpy
import os
import mathutils
import sys
import numpy as np

#from utils.mesh_creation import add_coarse_edges
import base64
#from utils.mergeObjects import merge_objects
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import subprocess
import app
import mathutils
from math import radians

# def parse_obj(file, tex_coords=False):
#     """
#     Load a mesh from an obj file

#     :param filename: path to the obj file
#     :param tex_coords: whether to load texture (UV) coordinates
#     :return: vertices: numpy array of shape (num_vertices, 3)
#     :return: faces: numpy array of shape (num_faces, 3)
#     """
#     vertices = []
#     faces = []
#     uvs = []
#     faces_uv = []

#     file=file.split('\n')
#     for line in file:
#         line_split = line.split()
#         if not line_split:
#             continue
#         elif tex_coords and line_split[0] == 'vt':
#             uvs.append([line_split[1], line_split[2]])
#         elif line_split[0] == 'v':
#             vertices.append([line_split[1], line_split[2], line_split[3]])
#         elif line_split[0] == 'f':
#             vertex_indices = [s.split("/")[0] for s in line_split[1:]]
#             faces.append(vertex_indices)
#             if tex_coords:
#                 uv_indices = [s.split("/")[1] for s in line_split[1:]]
#                 faces_uv.append(uv_indices)

#     vertices = np.array(vertices, dtype=np.float32)
#     faces = np.array(faces, dtype=np.int32) - 1

#     if tex_coords:
#         uvs = np.array(uvs, dtype=np.float32)
#         faces_uv = np.array(faces_uv, dtype=np.int32) - 1
#         return vertices, faces, uvs, faces_uv

#     return vertices, faces

# def obj2template2(file):
#     vertices, faces = parse_obj(file)
#     outer_trimesh = trimesh.Trimesh(vertices=vertices,
#                                     faces=faces, process=True)

#     vertices_proc = outer_trimesh.vertices
#     faces_proc = outer_trimesh.faces

#     out_dict = dict(vertices=vertices_proc, faces=faces_proc)
#     out_dict = add_coarse_edges(out_dict, 4)

#     return out_dict
BLENDER_PATH='blender'


#align_objects('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/garment.obj','/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/body.obj', 'aligned_output1.obj', 'aligned_output2.obj', 'aligned_output3.obj')
def align_objects(garment_path, body_path, output_pants_file, output_body_file, output_file, garment_type):
    # Construct the command to execute Blender with bpy script
    if garment_type==0:

        cmd = ['blender', "--background", "--python", "align_objects_pants.py", "--",
           garment_path, body_path, output_pants_file, output_body_file, output_file]
    elif garment_type==1:
        cmd = ['blender', "--background", "--python", "align_objects_shirt.py", "--",
           garment_path, body_path, output_pants_file, output_body_file, output_file]

    # Execute the command
    subprocess.run(cmd)

    # cmd = ['blender', "--b", "--python", "align_objects.py", "--",
    #        garment_path, body_path, output_pants_file, output_body_file, output_file]
    
    # # Execute the command
    # subprocess.run(cmd)

def merge_objects(garment_path, body_path, output_file):
    # Construct the command to execute Blender with bpy script
    cmd = ['blender', "--background", "--python", "mergeObjects.py", "--",
       garment_path, body_path, output_file]

    # Execute the command
    subprocess.run(cmd)

    # cmd = ['blender', "--b", "--python", "align_objects.py", "--",
    #        garment_path, body_path, output_pants_file, output_body_file, output_file]
    
    # # Execute the command
    # subprocess.run(cmd)

#align_objects('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/garment.obj', '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/body.obj', 'aligned_output1.obj', 'aligned_output2.obj', 'aligned_output3.obj')
###############################################################################################
@app.bpy_app.route('/run', methods=['POST'])
def align():
    data=request.get_json()
    garment_path = data['garment_path']
    body_path = data['body_path']
    garment_type = data['garment_type']
    print(body_path)
    align_objects(garment_path, body_path, 'garment_path.obj', 'body_path.obj', 'aligned_output3.obj', garment_type)
    return jsonify({'garment_path': 'garment_path.obj', 'body_path': 'body_path.obj', 'output_file': 'aligned_output3.obj'})


@app.bpy_app.route('/merge', methods=['POST'])
def merge():
    data=request.get_json()
    garment_path = data['garment_path']
    body_path = data['body_path']
    print(body_path)
    merge_objects(garment_path, body_path, 'merged_output.obj')
    return jsonify({'garment_path': 'garment_path.obj', 'body_path': 'body_path.obj', 'output_file': '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/merged_output.obj'})
    


if __name__ == "__main__":
    with app.bpy_app.app_context():
        app.db.create_all()
    app.bpy_app.run(host='localhost', port=5006, debug=True)
    #app.bpy_app.run(host='localhost', port=5007, debug=True)
###############################################################################################

