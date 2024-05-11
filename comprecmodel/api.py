import os
import random
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template, jsonify
import requests
from tensorflow.keras.applications import ResNet50
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

    #print("SHAALAN= " + image_path)

    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.resnet50.preprocess_input(img_array)
    return img_array

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

# Define Siamese network architecture
input_a = Input(shape=(224, 224, 3))
input_b = Input(shape=(224, 224, 3))

feat_extractor = Model(inputs=base_model.input, outputs=base_model.output)

# Flatten the feature maps
flatten = Flatten()

encoded_a = flatten(feat_extractor(input_a))
encoded_b = flatten(feat_extractor(input_b))

# Custom similarity metric (cosine similarity)
def cosine_similarity_metric(x):
    x[0] = tf.keras.backend.l2_normalize(x[0], axis=-1)
    x[1] = tf.keras.backend.l2_normalize(x[1], axis=-1)
    return tf.reduce_sum(tf.multiply(x[0], x[1]), axis=-1, keepdims=True)

similarity_score = Lambda(cosine_similarity_metric)([encoded_a, encoded_b])

# Siamese model
# siamese_model = Model(inputs=[input_a, input_b], outputs=similarity_score)

# Compile Siamese model with custom contrastive loss
#siamese_model.compile(loss=contrastive_loss, optimizer=Adam(lr=0.001))

# Load dataset
tops_folder = "/home/mahdy/new_garments/class1"
bottoms_folder = "/home/mahdy/new_garments/class2"

tops_images = [os.path.join(tops_folder, f) for f in os.listdir(tops_folder) if os.path.isfile(os.path.join(tops_folder, f))]
bottoms_images = [os.path.join(bottoms_folder, f) for f in os.listdir(bottoms_folder) if os.path.isfile(os.path.join(bottoms_folder, f))]

#siamese_model = tf.keras.models.load_model("siamese_model2.h5", custom_objects={'contrastive_loss': contrastive_loss, 'cosine_similarity_metric': cosine_similarity_metric})

# Example usage: Generate recommendations based on input image
def generate_recommendations(input_image_path, top_k=5):
    
    input_image = load_and_preprocess_image(input_image_path)
    input_features = flatten(feat_extractor(input_image))

    similarities = []
    for image_path in tops_images + bottoms_images:  # Combine both tops and bottoms images
        target_image = load_and_preprocess_image(image_path)
        target_features = flatten(feat_extractor(target_image))
        similarity = cosine_similarity_metric([input_features, target_features])
        similarities.append((image_path, similarity))

    similarities.sort(key=lambda x: x[1], reverse=False)
    return similarities[:top_k]

@app.comprec_app.route('/recommend' , methods=['GET'])
def recommend():

    data = request.get_json()

    if 'item_id' not in data:
        return jsonify({'message': 'Item id is required'})

    item = app.Item.query.filter_by(id=data['item_id']).first()

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
        if item is not None:
            item_data = {
                'id': item.id, 
                'item_name': item.item_name, 
                'description': item.description, 
                'front_image': item.front_image.decode('utf-8'), 
                'back_image': item.back_image.decode('utf-8'), 
            }
            items_list.append(item_data)


    return jsonify({'items': items_list})

    


if __name__ == "__main__":
    with app.comprec_app.app_context():
        app.db.create_all()
        

    app.comprec_app.run(host='localhost', port=5005, debug=True)    