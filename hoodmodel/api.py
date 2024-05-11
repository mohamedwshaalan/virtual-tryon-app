import os

HOOD_PROJECT = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/hoodmodel"
HOOD_DATA = "/home/mahdy/Desktop/HOOD_Model/hood_data/"

os.environ["HOOD_PROJECT"] = HOOD_PROJECT
os.environ["HOOD_DATA"] = HOOD_DATA
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

import app
print(os.getcwd())

# import tripy
import pickle

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
def parse_obj(file, tex_coords=False):
    """
    Load a mesh from an obj file

    :param filename: path to the obj file
    :param tex_coords: whether to load texture (UV) coordinates
    :return: vertices: numpy array of shape (num_vertices, 3)
    :return: faces: numpy array of shape (num_faces, 3)
    """
    vertices = []
    faces = []
    uvs = []
    faces_uv = []

    file=file.split('\n')
    for line in file:
        line_split = line.split()
        if not line_split:
            continue
        elif tex_coords and line_split[0] == 'vt':
            uvs.append([line_split[1], line_split[2]])
        elif line_split[0] == 'v':
            vertices.append([line_split[1], line_split[2], line_split[3]])
        elif line_split[0] == 'f':
            vertex_indices = [s.split("/")[0] for s in line_split[1:]]
            faces.append(vertex_indices)
            if tex_coords:
                uv_indices = [s.split("/")[1] for s in line_split[1:]]
                faces_uv.append(uv_indices)

    vertices = np.array(vertices, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32) - 1

    if tex_coords:
        uvs = np.array(uvs, dtype=np.float32)
        faces_uv = np.array(faces_uv, dtype=np.int32) - 1
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

#obj_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'polo_aligned.obj'
#out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'polo_aligned.pkl'
#waaait, just gime 5 mins

#template_dict = obj2template(obj_path)
#pickle_dump(template_dict, out_template_path)

modules, config = load_params('aux/from_any_pose')
dataloader_m, runner_module, runner, aux_modules = create_modules(modules, config)
dataloader = dataloader_m.create_dataloader()

checkpoint_path = '/home/mahdy/Desktop/HOOD_Model/hood_data/trained_models/postcvpr.pth'
state_dict =  torch.load(checkpoint_path)
runner.load_state_dict(state_dict['training_module'])
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
@app.hood_app.route('/api/hood/<outfit_id>/<user_id>/<outfit_id2>', methods=['GET'])
def run_hood(outfit_id, user_id, outfit_id2):
    # outfit=Outfit.query.filter_by(id=outfit_id).first()
    # top_item=Item.query.filter_by(id=outfit.top_id).first()
    # bottom_item=Item.query.filter_by(id=outfit.bottom_id).first()
    # user_id=outfit.user_id
    #current_user=User.query.filter_by(id=2).first()
    # top_garment_type_id=top_item.garment_type_id

    # outfit = app.Outfit.query.filter_by(id=outfit_id).first()

    # top = app.Item.query.filter_by(id=outfit.top_id).first()
    # bottom = app.Item.query.filter_by(id=outfit.bottom_id).first()

    #garment obj
    obj_file= app.GarmentType.query.filter_by(id=outfit_id).first().object_file
    #print(obj_file)
    decoded_obj_file = base64.b64decode(obj_file)
    #print(decoded_obj_file)
    decoded_obj_file_str = decoded_obj_file.decode('utf-8')
    #print(decoded_obj_file_str)
    #print(decoded_obj_file_str)

    
    
    
    template_dict = obj2template2(decoded_obj_file_str)
    print(template_dict.keys())
    save_obj("garment.obj", template_dict['vertices'], template_dict['faces'], template_dict['center'], template_dict['coarse_edges'])
    #body obj
    body_file= app.User.query.filter_by(id=user_id).first().body_model
    decoded_body_file = base64.b64decode(body_file)
    decoded_body_file_str = decoded_body_file.decode('utf-8')
    body_template_dict = obj2template2(decoded_body_file_str)
    print(body_template_dict)
    garment_path=os.path.join(os.getcwd(),'garment.obj')
    body_path=os.path.join(os.getcwd(),'body.obj')

    save_obj("body.obj", body_template_dict['vertices'], body_template_dict['faces'], body_template_dict['center'], body_template_dict['coarse_edges'])
    yaml_path=os.path.join(os.getcwd(),'configs/aux','from_any_pose.yaml')
    print(yaml_path)
    

    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    url='http://localhost:5006/run'
    request_data={'garment_path':garment_path,'body_path':body_path,'garment_type':0}
    response=requests.post(url,json=request_data)
    print(response.json())
    body_path=response.json()['body_path']
    garment_path=response.json()['garment_path']
    output_file=response.json()['output_file']
    template_dict_body = obj2template(os.path.join(os.getcwd(),body_path))
    out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'current_body.pkl'
    pickle_dump(template_dict_body, out_template_path)
    template_dict_garment = obj2template(os.path.join(os.getcwd(),garment_path))
    out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'current_garment.pkl'
    pickle_dump(template_dict_garment, out_template_path)
    data['dataloader']['dataset']['from_any_pose']['pose_sequence_path']='fromanypose/current_body.pkl'
    data['dataloader']['dataset']['from_any_pose']['garment_template_path']='fromanypose/current_garment.pkl'
    with open(yaml_path, 'w') as file:
        yaml.dump(data, file)
    






    # yaml_path=os.path.join(os.getcwd(),'configs/aux','from_any_pose.yaml')
    # print(yaml_path)
    # out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'current_garment.pkl'
    # pickle_dump(template_dict, out_template_path)

    # with open(yaml_path, 'r') as file:
    #     data = yaml.safe_load(file)

    # print(data)
    


    
    #user_body=current_user.body_model

    #run on top item
    #automate to remove the need for outfit_id
    #run on bottom item

    # data= request.get_json()
    # user_email = data['email']

    # outfit_id = data['outfit_id']
    #query database to get obj path
    

    sample = next(iter(dataloader))
    #print(template_dict)
    #print(sample)
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
    url='http://localhost:5006/merge'
    request_data={'garment_path':garment_path,'body_path':body_path}
    response=requests.post(url,json=request_data)
    merged_output=response.json()['output_file']
    ##Remove unnecessary files
    os.remove('obj_00000.obj')
    os.remove('obj_00001.obj')
    os.remove('body.obj')
    os.remove('garment.obj')
    os.remove('body_path.obj')
    os.remove('garment_path.obj')
    os.remove('aligned_output3.obj')
    os.remove('aligned_output3.mtl')


    # # # # #### shirt fitting
    obj_file= app.GarmentType.query.filter_by(id=outfit_id2).first().object_file
    #print(obj_file)
    decoded_obj_file = base64.b64decode(obj_file)
    #print(decoded_obj_file)
    decoded_obj_file_str = decoded_obj_file.decode('utf-8')
    #print(decoded_obj_file_str)
    #print(decoded_obj_file_str)s
    # 

    
    
    
    template_dict = obj2template2(decoded_obj_file_str)
    print(template_dict.keys())
    save_obj("garment.obj", template_dict['vertices'], template_dict['faces'], template_dict['center'], template_dict['coarse_edges'])
    yaml_path=os.path.join(os.getcwd(),'configs/aux','from_any_pose.yaml')
    print(yaml_path)
    

    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    url='http://localhost:5006/run'
    print(merged_output)
    request_data={'garment_path':'garment.obj','body_path':merged_output,'garment_type':1}
    response=requests.post(url,json=request_data)
    print(response.json())
    body_path=response.json()['body_path']
    garment_path=response.json()['garment_path']
    output_file=response.json()['output_file']
    template_dict_body = obj2template(os.path.join(os.getcwd(),body_path))
    print('Merged aligned: ',body_path)
    print('Garment aligned: ',garment_path)
    # os.remove('merged_output.obj')

    # out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'current_body.pkl'
    # #pickle_dump(template_dict_body, out_template_path)
    # convert_to_pkl(body_path, out_template_path)
    # template_dict_garment = obj2template(os.path.join(os.getcwd(),garment_path))
    # out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'current_garment.pkl'
    # pickle_dump(template_dict_garment, out_template_path)
    # data['dataloader']['dataset']['from_any_pose']['pose_sequence_path']='fromanypose/current_body.pkl'
    # data['dataloader']['dataset']['from_any_pose']['garment_template_path']='fromanypose/current_garment.pkl'
    # with open(yaml_path, 'w') as file:
    #     yaml.dump(data, file)
    # sample = next(iter(dataloader))
    # #print(template_dict)
    # #print(sample)
    # trajectories_dict = runner.valid_rollout(sample)
    # out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'shirt_fitting.pkl'
    # pickle_dump(dict(trajectories_dict), out_path)
    # out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'shirt_fitting.pkl'
    # out_video = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'shirt_fitting.mp4'
    # write_video(out_path, out_video, renderer)
    # # ### merge the body with the pants
    # garment_path=os.path.join(os.getcwd(),'obj_00000.obj')
    # body_path=os.path.join(os.getcwd(),'obj_00001.obj')
    # url='http://localhost:5006/merge'
    # request_data={'garment_path':garment_path,'body_path':body_path}
    # response=requests.post(url,json=request_data)
    # merged_output=response.json()['output_file']
    # ##Remove unnecessary files
    # os.remove('obj_00000.obj')
    # os.remove('obj_00001.obj')
    # #os.remove('body.obj')
    # os.remove('garment.obj')
    # os.remove('body_path.obj')
    # os.remove('garment_path.obj')
    # os.remove('aligned_output3.obj')
    # os.remove('aligned_output3.mtl')



    return jsonify({'message': 'HOOD API executed successfully'})


if __name__ == "__main__":
    with app.hood_app.app_context():
        app.db.create_all()
    app.hood_app.run(host='localhost', port=5004, debug=True)
