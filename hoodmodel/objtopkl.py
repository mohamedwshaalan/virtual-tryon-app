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
import pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import app

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
def pickle_to_base64(loadout):
    """
    Pickle the object and encode it as base64.
    """
    pickled_data = pickle.dumps(loadout)
    base64_data = base64.b64encode(pickled_data).decode('utf-8')
    return base64_data
def objtopkl(file):
    out_dict = obj2template2(file)
    pkl_file=pickle_to_base64(out_dict)
    #pickle_dump(out_dict, 'dump/template.pkl')
    pkl_db=app.GarmentType(garment_type='top', object_file=b'',pkl_file=pkl_file)
    app.db.session.add(pkl_db)
    app.db.session.commit()

#function to do that on the whole table
def objtopkl_all():
    for obj in app.GarmentType.query.all():
        objtopkl(obj.object_file)

##AGAIN IT IS NOT TESTED UNTIL NOW
##BUT IT SHOULD WORK FINE