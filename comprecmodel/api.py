import numpy as np
import pandas as pd
import os
import tensorflow as tf
import tensorflow.keras as keras
from keras import Model
from keras.applications.densenet import DenseNet121
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from keras.preprocessing import image
from keras.applications.densenet import preprocess_input, decode_predictions
from keras.layers import GlobalMaxPooling2D, Dense, GlobalAveragePooling2D
from sklearn.preprocessing import normalize
from keras.layers import GlobalMaxPooling2D
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import pathlib
from sklearn.metrics.pairwise import linear_kernel

from flask import Flask, request, render_template,  send_file, jsonify
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import app


class fashion_recommendations:
    """ Production class for recommendations of fashion from similarity """

    def __init__(self, img_path, df_embeddings):
        self.img_path = img_path
        self.df_embeddings = df_embeddings

    # Helper functions
    def load_model(self):
        """ Load our model """
        vgg16 = VGG16(include_top=False, weights='imagenet', input_shape=(100, 100, 3))
        vgg16.trainable=False
        vgg16_model = keras.Sequential([vgg16, GlobalMaxPooling2D()])
        return vgg16_model

    def predict(self, model, img_path):
        """ Load and preprocess image then make prediction """
        # Reshape
        img = image.load_img(self.img_path, target_size=(100, 100))
        # img to Array
        img = image.img_to_array(img)
        # Expand Dim (1, w, h)
        img = np.expand_dims(img, axis=0)
        # Pre process Input
        img = preprocess_input(img)
        return model.predict(img)

    #def preprocess_image(img_path):
    #    img = image.load_img(img_path, target_size=(img_width, img_height))
    #    img = image.img_to_array(img)
    #    img = np.expand_dims(img, axis=0)
    #    img = tf.keras.applications.vgg16.preprocess_input(img)
    #    return img

    def get_similarity(self):
        """ Get similarity of custom image """
        model = self.load_model()
        df_embeddings = self.df_embeddings
        sample_image = self.predict(model, self.img_path)
        df_sample_image = pd.DataFrame(sample_image)
        sample_similarity = linear_kernel(df_sample_image, df_embeddings)
        return sample_similarity

    def normalize_sim(self):
        """ Normalize similarity results """
        similarity = self.get_similarity()
        x_min = similarity.min(axis=1)
        x_max = similarity.max(axis=1)
        norm = (similarity-x_min)/(x_max-x_min)[:, np.newaxis]
        return norm

    def get_recommendations(self):
        """ Get recommended images """
        similarity = self.normalize_sim()

        # Get the pairwsie similarity scores of all clothes with that one (index, value)
        sim_scores = list(enumerate(similarity[0]))

        # Sort the clothes based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Get the scores of the 5 most similar clothes
        sim_scores = sim_scores[0:5]
        print(sim_scores)
        # Get the clothes indices
        cloth_indices = [i[0] for i in sim_scores]

        # Return the top 5 most similar products
        return cloth_indices

    def print_recommendations(self):
        """ Print the top 5 most similar products"""
        recommendation = self.get_recommendations()
        #recommendation_list = recommendation.tolist()
        #recommended images
        plt.figure(figsize=(20,20))
        j=0
        for i in recommendation:
            plt.subplot(6, 10, j+1)
            cloth_img =  mpimg.imread("../salmarecommendationmodel/fashion-dataset/images/" + str(i) + ".jpg")
            plt.imshow(cloth_img)
            plt.axis("off")
            j+=1
        plt.title("Recommended images",loc='left')
        plt.subplots_adjust(wspace=-0.5, hspace=1)
        plt.show()
        return

# Preprocess and load images
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(img_width, img_height))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = tf.keras.applications.vgg16.preprocess_input(img)
    return img


@app.comprec_app.route('/recommend' , methods=['GET'])
def recommend():
    img_path = request.args.get('img_path')
    df_embeddings = pd.read_csv('df_embeddings.csv')
    model = fashion_recommendations(img_path, df_embeddings)
    model.print_recommendations()
    return jsonify({'message': 'Recommendations generated successfully'})

if __name__ == "__main__":
    with app.comprec_app.app_context():
        app.db.create_all()
    app.comprec_app.run(host='localhost', port=5005, debug=True)

