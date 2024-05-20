import os
import pickle
import random
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template, jsonify
import requests
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications import ResNet152V2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Lambda, Flatten
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import base64

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import app

# Function to load and preprocess image
def load_and_preprocess_image(image_path):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, (224, 224))
    img = tf.keras.applications.resnet50.preprocess_input(img)
    img = tf.expand_dims(img, axis=0)
    return img

# Define custom contrastive loss function
def contrastive_loss(y_true, y_pred):
    margin = 1
    square_pred = tf.square(y_pred)
    margin_square = tf.square(tf.maximum(margin - y_pred, 0))
    
    # Ensure both y_true and y_pred have the same data type
    y_true = tf.cast(y_true, y_pred.dtype)
    
    return tf.reduce_mean(y_true * square_pred + (1 - y_true) * margin_square)

# Load pre-trained ResNet50 model without top layers    
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

feat_extractor = Model(inputs=base_model.input, outputs=base_model.output)

# Flatten the feature maps
flatten = Flatten()

# Custom similarity metric (cosine similarity)
def cosine_similarity_metric(x):
    x[0] = tf.keras.backend.l2_normalize(x[0], axis=-1)
    x[1] = tf.keras.backend.l2_normalize(x[1], axis=-1)
    return tf.reduce_sum(tf.multiply(x[0], x[1]), axis=-1, keepdims=True)

# Function to save embeddings to a file
def save_embeddings(embeddings, filename):
    with open(filename, 'wb') as f:
        pickle.dump(embeddings, f)

# Function to load embeddings from a file
def load_embeddings(filename):
    with open(filename, 'rb') as f:
        embeddings = pickle.load(f)
    return embeddings

# Load dataset using tf.data.Dataset for efficient processing
tops_folder = "/home/mahdy/new_garments/class1"
bottoms_folder = "/home/mahdy/new_garments/class2"

# tops_images = [os.path.join(tops_folder, f) for f in os.listdir(tops_folder) if os.path.isfile(os.path.join(tops_folder, f))]
# bottoms_images = [os.path.join(bottoms_folder, f) for f in os.listdir(bottoms_folder) if os.path.isfile(os.path.join(bottoms_folder, f))]

# Example usage
embeddings_filename = "embeddings.pkl"

# Function to load embeddings and generate recommendations
def load_embeddings_and_generate_recommendations(input_image_path, embeddings_filename, top_k=5):
    embeddings = load_embeddings(embeddings_filename)
    input_image = load_and_preprocess_image(input_image_path)
    input_features = flatten(feat_extractor(input_image))

    similarities = []
    for image_path, features in embeddings.items():
        similarity = cosine_similarity_metric([input_features, features])
        similarities.append((image_path, similarity))

    similarities.sort(key=lambda x: x[1], reverse=False)
    return similarities[:top_k]

# Example usage: Generate recommendations based on input image
def generate_recommendations(input_image_path, top_k=5):
    return load_embeddings_and_generate_recommendations(input_image_path, embeddings_filename, top_k)

# Function to load embeddings and generate recommendations
def load_embeddings_for_you(input_image_path, embeddings_filename, top_k=5):
    embeddings = load_embeddings(embeddings_filename)
    input_image = load_and_preprocess_image(input_image_path)
    input_features = flatten(feat_extractor(input_image))

    similarities = []
    for image_path, features in embeddings.items():
        similarity = cosine_similarity_metric([input_features, features])
        similarities.append((image_path, similarity))


    similarities.sort(key=lambda x: x[1], reverse=True)

    #remove first element as it is the input image itself
    similarities.pop(0)
    return similarities[:top_k]

# Example usage: Generate recommendations based on input image
def fyp(input_image_path, top_k=1):
    return load_embeddings_for_you(input_image_path, embeddings_filename, top_k)

@app.comprec_app.route('/recommend' , methods=['GET'])
def recommend():

    #data = request.get_json()

    item_id = request.args.get('item_id')
    
    # if 'item_id' not in data:
    #     return jsonify({'message': 'Item id is required'})
    
    #item = app.Item.query.filter_by(id=data['item_id']).first()
    item = app.Item.query.filter_by(id=item_id).first()


    if item is None:
        return jsonify({'message': 'Item not found'})


    base64_string = item.front_image.decode('utf-8')

    image_data = base64.b64decode(base64_string)

    with open('dump/temp.jpg', 'wb') as f:
        f.write(image_data)

    input_image_path = 'dump/temp.jpg'


    recommendations = generate_recommendations(input_image_path)

    images = []
    for idx, (image_path, similarity) in enumerate(recommendations):
        images.append(image_path)
    

    items_list = []
    for image in images:
        item = app.Item.query.filter_by(file_name=image.split('/')[-1]).first()
        print(item.vendor_id)
        vendor = app.Vendor.query.filter_by(id=item.vendor_id).first()
        if item is not None:
            item_data = {
                'id': item.id,
                'item_name': item.item_name,
                'description': item.description,
                'front_image': item.front_image.decode('utf-8'),
                'back_image': item.back_image.decode('utf-8'),
                'texture': item.texture.decode('utf-8'),
                'vendor': vendor.vendor_name,
                'vendor_link': vendor.vendor_link,
                'garment_type': 'top' if item.garment_type_id in (1, 2, 3) else 'bottom'
            }
            
            items_list.append(item_data)


    return jsonify({'items': items_list})

@app.comprec_app.route('/recommend_for_you', methods=['GET'])
def recommend_for_you():
    user_id = request.args.get('user_id')

    # Get first 5 user favorites
    likes = app.Likes.query.filter_by(user_id=user_id).limit(5).all()

    recommendations = []

    # Iterate over likes and get recommended items
    for like in likes:
        item = app.Item.query.filter_by(id=like.item_id).first()
        if item:
            base64_string = item.front_image.decode('utf-8')
            image_data = base64.b64decode(base64_string)
            
            with open('dump/temp.jpg', 'wb') as f:
                f.write(image_data)

            input_image_path = 'dump/temp.jpg'

            recommendations.extend(fyp(input_image_path))

    # Extract image paths from recommendations
    images = [image_path for image_path, _ in recommendations]

    items_list = []
    for image_path in images:
        item = app.Item.query.filter_by(file_name=image_path.split('/')[-1]).first()
        if item:
            vendor = app.Vendor.query.filter_by(id=item.vendor_id).first()
            item_data = {
                'id': item.id,
                'item_name': item.item_name,
                'description': item.description,
                'front_image': item.front_image.decode('utf-8'),
                'back_image': item.back_image.decode('utf-8'),
                'texture': item.texture.decode('utf-8'),
                'vendor': vendor.vendor_name,
                'vendor_link': vendor.vendor_link,
                'garment_type': 'top' if item.garment_type_id in (1, 2, 3) else 'bottom'
            }
            items_list.append(item_data)

    return jsonify({'items': items_list})

    


if __name__ == "__main__":
    with app.comprec_app.app_context():
        app.db.create_all()
        

    app.comprec_app.run(host='localhost', port=5005, debug=True)    