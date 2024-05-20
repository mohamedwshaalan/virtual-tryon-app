import os

HOOD_PROJECT = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel"
HOOD_DATA = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel/hooddata"

os.environ["HOOD_PROJECT"] = HOOD_PROJECT
os.environ["HOOD_DATA"] = HOOD_DATA
import aspose.threed as a3d

import trimesh
from utils.mesh_creation import obj2template
from pathlib import Path
from utils.defaults import DEFAULTS
from utils.common import move2device, pickle_dump
from utils.validation import Config as ValidationConfig
from utils.arguments import load_params, create_modules
from utils.arguments import load_params
from utils.common import move2device, pickle_dump
from utils.defaults import DEFAULTS
#from utils.mergeObjects import merge_objects
from pathlib import Path
import torch
import shutil
from utils.show import write_video 
from aitviewer.headless import HeadlessRenderer
from pathlib import Path
from utils.defaults import DEFAULTS
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from utils.mesh_creation import add_coarse_edges
#from main import GarmentType,User,db,Outfit,Item
import base64
import numpy as np
import trimesh
import sys
import yaml
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import time
import app

print(os.getcwd())

# import tripy
import pickle

def save_decoded_image_from_base64(base64_string, output_path):
    try:
        # Decode the base64 string
        decoded_image = base64.b64decode(base64_string)
        
        # Write the decoded image data to the output file
        with open(output_path, "wb") as output_file:
            output_file.write(decoded_image)
        
        print("Image successfully saved to:", output_path)
    except Exception as e:
        print("Error occurred:", str(e))
def load_obj(file_path):
    verts = []
    faces = []

    with open(file_path, 'r') as file:
        for line in file:
            tokens = line.strip().split()
            if not tokens:
                continue

            if tokens[0] == 'v':
                verts.append([float(tokens[1]), float(tokens[2]), float(tokens[3])])
            elif tokens[0] == 'f':
                face = [int(vertex.split('/')[0]) - 1 for vertex in tokens[1:]]
                faces.append(face)

    return np.array(verts), np.array(faces)

def convert_to_pkl(obj_file, output_pkl):
    verts, faces = load_obj(obj_file)

    mesh_data = {'vertices': verts, 'faces': faces}

    with open(output_pkl, 'wb') as pkl_file:
        pickle.dump(mesh_data, pkl_file)




def parse_obj(file_content, tex_coords=True):
    """
    Load a mesh from an obj file content

    :param file_content: content of the obj file as a string
    :param tex_coords: whether to load texture (UV) coordinates
    :return: vertices: numpy array of shape (num_vertices, 3)
    :return: faces: numpy array of shape (num_faces, 3)
    :return: uvs: numpy array of shape (num_uv_coords, 2) (if tex_coords is True)
    :return: faces_uv: numpy array of shape (num_faces, 3) (if tex_coords is True)
    """
    vertices = []
    faces = []
    uvs = []
    faces_uv = []

    file_content = file_content.split('\n')
    for line in file_content:
        line_split = line.split()
        if not line_split:
            continue
        elif tex_coords and line_split[0] == 'vt':
            uvs.append([float(line_split[1]), float(line_split[2])])
        elif line_split[0] == 'v':
            vertices.append([float(line_split[1]), float(line_split[2]), float(line_split[3])])
        elif line_split[0] == 'f':
            vertex_indices = [int(s.split("/")[0]) - 1 for s in line_split[1:]]
            faces.append(vertex_indices)
            if tex_coords:
                uv_indices = [int(s.split("/")[1]) - 1 for s in line_split[1:] if len(s.split("/")) > 1]

                faces_uv.append(uv_indices)

    vertices = np.array(vertices, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)

    if tex_coords:
        uvs = np.array(uvs, dtype=np.float32)
        faces_uv = np.array(faces_uv, dtype=np.int32)
        return vertices, faces, uvs, faces_uv

    return vertices, faces



def obj2template2(file):
    vertices, faces = parse_obj(file)
    outer_trimesh = trimesh.Trimesh(vertices=vertices,
                                    faces=faces, process=True)

    vertices_proc = outer_trimesh.vertices
    faces_proc = outer_trimesh.faces

    out_dict = dict(vertices=vertices_proc, faces=faces_proc)
    out_dict = add_coarse_edges(out_dict, 4)

    return out_dict


def save_obj(filename, vertices, faces, center, coarse_edges):
    with open(filename, 'w') as f:
        # Write vertices
        for vertex in vertices:
            f.write("v {} {} {}\n".format(vertex[0], vertex[1], vertex[2]))

        # Write center
        if len(center) == 3:
            f.write("c {} {} {}\n".format(center[0], center[1], center[2]))
        elif len(center) == 2:
            f.write("c {} {}\n".format(center[0], center[1]))
        else:
            print("Invalid center:", center)
        

        # Write faces
        for face in faces:
            f.write("f")
            for vertex_index in face:
                f.write(" {}".format(vertex_index + 1))
            f.write("\n")

        # Write coarse edges
        for edge in coarse_edges:
            if isinstance(edge, (list, tuple)) and len(edge) == 2:
                f.write("ce {} {}\n".format(edge[0] + 1, edge[1] + 1))
            else:
                print("Invalid coarse edge:", edge)


def save_obj_with_uv(vertices, faces, uvs,faces_uv, filename):
    with open(filename, 'w') as f:
        # Write vertices
        for v in vertices:
            f.write("v {} {} {}\n".format(v[0], v[1], v[2]))

        # Write UV coordinates
        for uv in uvs:
            f.write("vt {} {}\n".format(uv[0], uv[1]))

        # Write faces with UV indices
        for face, face_uv in zip(faces, faces_uv):
            f.write("f")
            for vertex_idx, uv_idx in zip(face, face_uv):
                f.write(" {}/{}".format(vertex_idx + 1, uv_idx + 1))  # Indices are 1-based in OBJ files
            f.write("\n")
def save_parsed_data(mesh, output_file='parsed.obj'):
    mesh.export(output_file)


import io
@app.hood_app.route('/api/hood/<outfit_id>/<user_id>/<size>', methods=['GET'])
def run_hood(outfit_id, user_id, size):
    
    if os.path.exists('final_video.mp4'):
        os.remove('final_video.mp4')
    item1=app.Outfit.query.filter_by(id=outfit_id).first().top_id
    item2=app.Outfit.query.filter_by(id=outfit_id).first().bottom_id
    garment_type_id1=app.Item.query.filter_by(id=item1).first().garment_type_id
    garment_type_id2=app.Item.query.filter_by(id=item2).first().garment_type_id
    height=app.User.query.filter_by(id=user_id).first().height
    garment_type1=app.GarmentType.query.filter_by(id=garment_type_id1).first().garment_type
    garment_type2=app.GarmentType.query.filter_by(id=garment_type_id2).first().garment_type
    token1=''
    token2=''
    if height>=160 and height<=170:
        token1='Short'
    elif height>170 and height<=180:
        token1='Average'
    elif height>180:
        token1='Tall'
    
    
    if int(size)==0:
        token2='Small'
    elif int(size)==1:
        token2='Medium'
    elif int(size)==2:
        token2='Large'
    elif int(size)==3:
        token2='XL'
    print(size)
    print(token2)

    garment_type1=token2+'_'+token1+'_'+garment_type1
    garment_type2=token2+'_'+token1+'_'+garment_type2

    print(garment_type1)
    print(garment_type2)

    



    #garment obj
    file_paths = [
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_body.pkl',
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_garment.pkl',
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_body2.pkl',
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_garment2.pkl'
]

    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"File '{file_path}' does not exist, skipping removal.")
    obj_file= app.GarmentType.query.filter_by(garment_type=garment_type2).first().object_file
    
    decoded_obj_file = base64.b64decode(obj_file)
    
    decoded_obj_file_str = decoded_obj_file.decode('latin1')
    
    vertices, faces,uvs, faces_uv = parse_obj(decoded_obj_file_str)
    
    save_obj_with_uv(vertices, faces, uvs, faces_uv, 'garment.obj')
    

    

    
    
    
    
    #body obj
    body_file= app.User.query.filter_by(id=user_id).first().body_model
    decoded_body_file = base64.b64decode(body_file)
    decoded_body_file_str = decoded_body_file.decode('utf-8')
    vertices, faces,_,_ = parse_obj(decoded_body_file_str)
    outer_trimesh = trimesh.Trimesh(vertices=vertices,
                                    faces=faces, process=True)
    outer_trimesh.export('body.obj')
    
    
    garment_path=os.path.join(os.getcwd(),'garment.obj')
    body_path=os.path.join(os.getcwd(),'body.obj')

    
    url='http://localhost:5006/run'
    request_data={'garment_path':garment_path,'body_path':body_path,'garment_type':0}
    response=requests.post(url,json=request_data)
    print(response.json())
    body_path=response.json()['body_path']
    garment_path=response.json()['garment_path']
    output_file=response.json()['output_file']
    print(body_path)
    
    


    
    out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_body.pkl'
    convert_to_pkl(body_path, out_template_path)
    
    print(garment_path)
    
    out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_garment.pkl'
    convert_to_pkl(garment_path, out_template_path)
    
    






    
    #query database to get obj path
    
    modules, config = load_params('aux/from_any_pose')
    dataloader_m, runner_module, runner, aux_modules = create_modules(modules, config)
    dataloader = dataloader_m.create_dataloader()
    
    checkpoint_path = '/home/mahdy/Desktop/HOOD_Model/hood_data/trained_models/postcvpr.pth'
    state_dict =  torch.load(checkpoint_path)
    runner.load_state_dict(state_dict['training_module'])

    

    sample = next(iter(dataloader))
    
    trajectories_dict = runner.valid_rollout(sample)
    out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'polo_fitting.pkl'
    pickle_dump(dict(trajectories_dict), out_path) #store in database
    renderer = HeadlessRenderer()
    out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'polo_fitting.pkl'
    out_video = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'polo_fitting.mp4'
    write_video(out_path, out_video, renderer)
    # ### merge the body with the pants
    garment_path=os.path.join(os.getcwd(),'obj_00000.obj')
    body_path=os.path.join(os.getcwd(),'obj_00001.obj')
    
    #apply texture to pants
    texture=app.Item.query.filter_by(id=item2).first().texture
    texture_path=os.path.join(os.getcwd(),'texture1.jpg')
    save_decoded_image_from_base64(texture,texture_path)
    url='http://localhost:5006/apply_texture'
    request_data={'cloth2tex_tshirt_path':'garment.obj','hood_tshirt_path':garment_path,'output_tshirt_file':'pants_tex.obj','image_path':'texture1.jpg'}
    response=requests.post(url,json=request_data)
    print(response.json())
    
    url='http://localhost:5006/merge'
    request_data={'garment_path':garment_path,'body_path':body_path}
    response=requests.post(url,json=request_data)
    merged_output=response.json()['output_file']
    shutil.copy('obj_00001.obj', 'fit_body.obj')
    ##Remove unnecessary files
    
    os.remove('body_path.obj')
    os.remove('garment_path.obj')
    os.remove('aligned_output3.obj')
    os.remove('aligned_output3.mtl')
    file_paths = [
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_body.pkl',
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_garment.pkl',
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_body2.pkl',
    Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_garment2.pkl'
]

    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"File '{file_path}' does not exist, skipping removal.")
    


    # # # # #### shirt fitting
    obj_file= app.GarmentType.query.filter_by(garment_type=garment_type1).first().object_file
    
    decoded_obj_file = base64.b64decode(obj_file)
    
    decoded_obj_file_str = decoded_obj_file.decode('latin')
    
    
    vertices, faces,uvs, faces_uv = parse_obj(decoded_obj_file_str)
    print('UVs and faces UV garment:')
    print(uvs)
    print(faces_uv)
    save_obj_with_uv(vertices, faces, uvs, faces_uv, 'garment.obj')
   

    
    
    
    
    
    url='http://localhost:5006/run'
    print(merged_output)
    request_data={'garment_path':'garment.obj','body_path':merged_output,'garment_type':1}
    response=requests.post(url,json=request_data)
    print(response.json())
    body_path=response.json()['body_path']
    garment_path=response.json()['garment_path']
    output_file=response.json()['output_file']
    
    print('Merged aligned: ',body_path)
    print('Garment aligned: ',garment_path)
    
    out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_body.pkl'
    
    convert_to_pkl(body_path, out_template_path)
    time.sleep(10)  # This will pause the execution for 10 seconds
    out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'new_current_garment.pkl'
    convert_to_pkl(garment_path, out_template_path)
    

    
    modules, config = load_params('aux/from_any_pose')
    dataloader_m, runner_module, runner, aux_modules = create_modules(modules, config)
    dataloader = dataloader_m.create_dataloader()
    
    checkpoint_path = '/home/mahdy/Desktop/HOOD_Model/hood_data/trained_models/postcvpr.pth'
    state_dict =  torch.load(checkpoint_path)
    runner.load_state_dict(state_dict['training_module'])
    sample = next(iter(dataloader))
    
    trajectories_dict = runner.valid_rollout(sample)
    out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'shirt_fitting.pkl'
    pickle_dump(dict(trajectories_dict), out_path)
    out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'shirt_fitting.pkl'
    out_video = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'shirt_fitting.mp4'
    write_video(out_path, out_video, renderer)
    
    #get texture
    texture=app.Item.query.filter_by(id=item1).first().texture
    texture_path=os.path.join(os.getcwd(),'texture2.jpg')
    save_decoded_image_from_base64(texture,texture_path)
    url='http://localhost:5006/apply_texture'

    request_data={'cloth2tex_tshirt_path':'garment.obj','hood_tshirt_path':'obj_00000.obj','output_tshirt_file':'tshirt_tex.obj','image_path':texture_path}
    response=requests.post(url,json=request_data)
    print(response.json())
    output_tshirt_file=response.json()['output_tshirt_file']
    #merge the body with the pants
    url='http://localhost:5006/merge'
    request_data={'garment_path':'pants_tex.obj','body_path':'fit_body.obj'}
    response=requests.post(url,json=request_data)
    merged_output=response.json()['output_file']
    ##adjust location
    url='http://localhost:5006/locate'
    request_data={'path_to_first_obj':'obj_00001.obj','path_to_second_obj':'fit_body.obj','path_to_third_obj':'pants_tex.obj','path_to_fourth_obj':'tshirt_tex.obj','output_file':'final_body.obj','output_file_body':'new_body.obj','output_file_pants':'new_pants.obj','output_file_tshirt':'new_tshirt.obj'}
    response=requests.post(url,json=request_data)
    print(response.json())





    #generate video
    url='http://localhost:5006/create_video'
    request_data={'object_file':'final_body.obj'}
    response=requests.post(url,json=request_data)
    print(response.json())
   

    for file in os.listdir(os.getcwd()):
        if (file.endswith('.obj')):
            os.remove(file)

    os.remove('texture1.jpg')
    os.remove('texture2.jpg')
    if os.path.exists('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/meshes/video.mp4'):
        os.remove('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/meshes/video.mp4')
    shutil.copy('final_video.mp4', '/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/meshes/video.mp4')
    




    return jsonify({'message': 'HOOD API executed successfully'})


if __name__ == "__main__":
    with app.hood_app.app_context():
        app.db.create_all()
    app.hood_app.run(host='localhost', port=5004, debug=True)
