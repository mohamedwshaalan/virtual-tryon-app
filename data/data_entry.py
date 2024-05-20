import csv
import base64
import os
from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd

garment_type_mapping = {
    "Tshirt": 1,
    "Trouser": 2,
    "Polo": 3,
    "Shorts": 4,
    "Jacket": 5
}

#GET ITEM
@app.data_app.route('/item/<item_id>', methods=['GET'])
def get_item(item_id):

    item = app.Item.query.filter_by(id=item_id).first()

    item_data = {
        'id': item.id, 
        'item_name': item.item_name, 
        'description': item.description, 
        'front_image': item.front_image.decode('utf-8'), 
        'back_image': item.back_image.decode('utf-8'), 
        'texture': item.texture.decode('utf-8'), 
    }
    return jsonify({'item': item_data})

#SEARCH FOR SIMILAR ITEMS
@app.data_app.route('/search', methods=['GET'])
def search():
    data = request.get_json()
    search_query = data.get('query')
    if not search_query:
        return jsonify({'message': 'No search query provided'})

    items = app.Item.query.all()
    item_ids = []
    item_captions = []
    for item in items:
        item_ids.append(item.id)
        item_captions.append(item.caption)
    df = pd.DataFrame({'item_id': item_ids, 'item_caption': item_captions})
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['item_caption'])
    target_tfidf = vectorizer.transform([search_query])
    similarities = cosine_similarity(target_tfidf, tfidf_matrix)

    num_similarities = 5
    top_indices = similarities.argsort()[0, :-num_similarities-1:-1]

    top_similarities = df.iloc[top_indices]

    top_ids = top_similarities['item_id'].tolist()

    output = []
    for item_id in top_ids:
        item = app.Item.query.filter_by(id=item_id).first()
    
        item_data = {
            'id': item.id, 
            'item_name': item.item_name, 
            'description': item.description, 
            'front_image': item.front_image.decode('utf-8'), 
            'back_image': item.back_image.decode('utf-8'), 
            'texture': item.texture.decode('utf-8'), 

        }
        output.append(item_data)
    return jsonify({'items': output})
    
def read_obj_file(obj_file_path):
    """
    Read an OBJ file from its path.

    :param obj_file_path: Path to the OBJ file
    :return: Content of the OBJ file as a string
    """
    with open(obj_file_path, 'r') as file:
        obj_file_content = file.read()
    
    return obj_file_content


# Function to encode image to base64
def encode_image(filename):
    path = filename + ".jpg" 
    with open(path, 'rb') as image_file:
        return base64.b64encode(image_file.read()) 

vendor_mapping = {
    "Zara": 1,
    "Pull&Bear": 2,
}
import numpy as np
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
with app.data_app.app_context():  #UNCOMMENT TO POPULATE DB
#     app.db.drop_all()
#     app.db.create_all()
#     with open('Database.csv', 'r', encoding = 'utf8') as file:
#         reader = csv.reader(file)
#         next(reader)  
#         for row in reader:
#             item_name, description, front_image_name, back_image_name, vendor_name, link, garment_type, caption= row
#             link = link.replace('\n', '')
#             garment_type_id = garment_type_mapping.get(garment_type, 0)
#             vendor_id = vendor_mapping.get(vendor_name, 0)
#             item = app.Item(item_name=item_name, description=description, garment_type_id=garment_type_id, front_image=encode_image(front_image_name), back_image=encode_image(back_image_name), texture=b'', 
#             vendor_id=vendor_id, item_link=link, caption = caption, file_name = front_image_name + ".jpg") 
#             app.db.session.add(item)   

#     #add vendor Zara and Pull&Bear
#     zara = app.Vendor(vendor_name="Zara", vendor_link="https://www.zara.com/")
#     app.db.session.add(zara)
#     pull_bear = app.Vendor(vendor_name="Pull&Bear", vendor_link="https://www.pullandbear.com/")
#     app.db.session.add(pull_bear)

#     #add garment types
#     #get Tshirt.obj 
#     tshirt_obj = open('Tshirt.obj', 'rb').read()
#     tshirt_obj = base64.b64encode(tshirt_obj)
#     tshirt = app.GarmentType(garment_type="Tshirt", object_file=tshirt_obj)
#     app.db.session.add(tshirt)

#     trouser_obj = open('Trousers.obj', 'rb').read()
#     trouser_obj = base64.b64encode(trouser_obj)
#     trouser = app.GarmentType(garment_type="Trousers", object_file=trouser_obj)
#     app.db.session.add(trouser)
    # Example usage:
    # obj_file_path = "/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Tshirt/Medium_Tall.obj"
    # obj_file_content = read_obj_file(obj_file_path)
    # print(obj_file_content)
    # vertices, faces, uvs, faces_uv = parse_obj(obj_file_content, tex_coords=True)
    # print(uvs)
    # print(faces_uv)
    # polo_obj = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Tshirt/Medium_Tall.obj', 'rb').read()
    # print(polo_obj)
    # polo_obj = base64.b64encode(polo_obj)
    # polo = app.GarmentType(garment_type="Polo", object_file=polo_obj)
    # app.db.session.add(polo)

#     shorts_obj = open('Shorts.obj', 'rb').read()
#     shorts_obj = base64.b64encode(shorts_obj)
#     shorts = app.GarmentType(garment_type="Shorts", object_file=shorts_obj)
#     app.db.session.add(shorts)

    # jacket_obj = open('/home/mahdy/Desktop/resized_garments/jacket/jacket_aligned.obj', 'rb').read()
    # jacket_obj = base64.b64encode(jacket_obj)
    # jacket = app.GarmentType(garment_type="Jacket2", object_file=jacket_obj)
    # app.db.session.add(jacket)
    # app.db.session.commit()

#     # medium_tall_pants_obj = open('Medium_Tall.obj', 'rb').read()
#     # medium_tall_pants_obj = base64.b64encode(medium_tall_pants_obj)
#     # medium_tall_pants = app.GarmentType(garment_type="Medium_Tall", object_file=medium_tall_pants_obj)

#     # app.db.session.add(medium_tall_pants)


#     # medium_tall_tshirt_obj = open('Medium_Tall_Tshirt.obj', 'rb').read()
#     # medium_tall_tshirt_obj = base64.b64encode(medium_tall_tshirt_obj)
#     # medium_tall_tshirt = app.GarmentType(garment_type="Medium_Tall_Tshirt", object_file=medium_tall_tshirt_obj)

#     # app.db.session.add(medium_tall_tshirt)


#     #add user
#     #get body.obj file
#     body_obj = open('/home/mahdy/Desktop/pants&body/body_examples/tall.obj', 'rb').read()
#     body_obj = base64.b64encode(body_obj)


#     user = app.User(email = 'email 2', password = 'password 2', first_name = 'first name 2', body_model=body_obj, weight=68, height=177, gender = "female")
#     app.db.session.add(user)
            
#     #create outfit for user
#     #outfit = app.Outfit(name='Outfit 1', user_id=1, top_id=1, bottom_id=2)

#    #open Garment_Objects/Jackets and read any file ending in .obj
#     for file in os.listdir('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Jackets'):
#         if file.endswith(".obj"):
#             obj = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Jackets/' + file, 'rb').read()
#             obj = base64.b64encode(obj)
#             #remove .obj from file name
#             file = file[:-4]
#             garment = app.GarmentType(garment_type= file + "_Jacket", object_file=obj)
#             app.db.session.add(garment)

#     # now do the same for Pants, Polo, Shorts, Tshirt
#     for file in os.listdir('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Pants'):
#         if file.endswith(".obj"):
#             obj = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Pants/' + file, 'rb').read()
#             obj = base64.b64encode(obj)
#             #remove .obj from file name
#             file = file[:-4]
#             garment = app.GarmentType(garment_type= file + "_Pants", object_file=obj)
#             app.db.session.add(garment)
    
#     for file in os.listdir('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Polo'):
#         if file.endswith(".obj"):
#             obj = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Polo/' + file, 'rb').read()
#             obj = base64.b64encode(obj)
#             #remove .obj from file name
#             file = file[:-4]
#             garment = app.GarmentType(garment_type= file + "_Polo", object_file=obj)
#             app.db.session.add(garment)
    
#     for file in os.listdir('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Shorts'):
#         if file.endswith(".obj"):
#             obj = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Shorts/' + file, 'rb').read()
#             obj = base64.b64encode(obj)
#             #remove .obj from file name
#             file = file[:-4]
#             garment = app.GarmentType(garment_type= file + "_Shorts", object_file=obj)
#             app.db.session.add(garment)

#     for file in os.listdir('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Tshirt'):
#         if file.endswith(".obj"):
#             obj = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/Garment_Objects/Tshirt/' + file, 'rb').read()
#             obj = base64.b64encode(obj)
#             #remove .obj from file name
#             file = file[:-4]
#             garment = app.GarmentType(garment_type= file + "_Tshirt", object_file=obj)
#             app.db.session.add(garment)

    # outfit = app.Outfit(name='Outfit 1', user_id=1, top_id=1, bottom_id=206)
    # app.db.session.add(outfit)

    # # get the texture file from '/home/mahdy/Downloads/0_texture_uv_1000(1)' 
    # texture = open('/home/mahdy/Downloads/0_texture_uv_1000(1).jpg', 'rb').read()
    # # get the  image from data/TshirtFront144.jpg
    # front_image = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/TshirtFront144.jpg', 'rb').read()
    # # get the  image from data/TshirtBack144.jpg
    # back_image = open('/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/data/TshirtBack144.jpg', 'rb').read()
    # # get the  image from data/TshirtFront144.jpg
    # texture = base64.b64encode(texture)
    # front_image = base64.b64encode(front_image)
    # back_image = base64.b64encode(back_image)
    # # add the item to the database
    # item = app.Item(item_name='Tshirt', description='Tshirt', front_image=front_image, back_image=back_image, 
    #                 texture=texture, vendor_id=1, garment_type_id=1, caption='Tshirt', file_name='TshirtFront144.jpg')

    texture = open('/home/mahdy/Downloads/0_texture_uv_1000(4).jpg', 'rb').read()
    texture = base64.b64encode(texture)
    item=app.Item(item_name='Pants',description='Pants',front_image=b'',back_image=b'',texture=texture,vendor_id=1,garment_type_id=20,caption='Pants',file_name='')
    app.db.session.add(item)

    app.db.session.commit()
    

if __name__ == '__main__':
    with app.data_app.app_context():
        app.db.create_all() 
        
    app.data_app.run(debug=True)