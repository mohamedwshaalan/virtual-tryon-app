import os

HOOD_PROJECT = "/home/mahdy/Desktop/virtual_tryon_app_main/hoodmodel"
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

#template_dict = obj2template(obj_path)
#pickle_dump(template_dict, out_template_path)

modules, config = load_params('aux/from_any_pose')
dataloader_m, runner_module, runner, aux_modules = create_modules(modules, config)
dataloader = dataloader_m.create_dataloader()

checkpoint_path = '/home/mahdy/Desktop/HOOD_Model/hood_data/trained_models/postcvpr.pth'
state_dict =  torch.load(checkpoint_path)
runner.load_state_dict(state_dict['training_module'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#select obj from user where email=
class GarmentType(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    garment_type = db.Column(db.String(150), nullable=False)
    object_file = db.Column(db.LargeBinary)
    
@app.route('/api/hood/<outfit_id>', methods=['GET'])
def run_hood(outfit_id):
    # outfit=Outfit.query.filter_by(id=outfit_id).first()
    # top_item=Item.query.filter_by(id=outfit.top_id).first()
    # bottom_item=Item.query.filter_by(id=outfit.bottom_id).first()
    # user_id=outfit.user_id
    #current_user=User.query.filter_by(id=2).first()
    # top_garment_type_id=top_item.garment_type_id
    obj_file=GarmentType.query.filter_by(id=outfit_id).first().object_file
    #print(obj_file)
    decoded_obj_file = base64.b64decode(obj_file)
    #print(decoded_obj_file)
    decoded_obj_file_str = decoded_obj_file.decode('utf-8')
    #print(decoded_obj_file_str)
    # 
    out_template_path = Path(DEFAULTS.data_root) / 'fromanypose' / 'polo_aligned.pkl'
    template_dict = obj2template2(decoded_obj_file_str)
    pickle_dump(template_dict, out_template_path)
    
    #user_body=current_user.body_model

    #run on top item
    #automate to remove the need for outfit_id
    #run on bottom item

    # data= request.get_json()
    # user_email = data['email']

    # outfit_id = data['outfit_id']
    #query database to get obj path
    

    sample = next(iter(dataloader))
    #print(sample)
    trajectories_dict = runner.valid_rollout(sample)
    out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'polo_fitting.pkl'
    pickle_dump(dict(trajectories_dict), out_path) #store in database
    renderer = HeadlessRenderer()
    out_path = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'polo_fitting.pkl'
    out_video = Path(DEFAULTS.data_root) / 'temp' / 'our_results' / 'polo_fitting.mp4'
    write_video(out_path, out_video, renderer)
    return jsonify({'message': 'HOOD API executed successfully'})

if __name__ == '__main__':
    app.run()
