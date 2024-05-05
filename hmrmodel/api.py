from flask import Flask, request, render_template, jsonify
import requests
from inference import DeepLabModel
import os
import tensorflow as tf
from six.moves import urllib
import numpy as np
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import app


MODEL_NAME = 'xception_coco_voctrainval' 

_DOWNLOAD_URL_PREFIX = 'http://download.tensorflow.org/models/'
_MODEL_URLS = {
	'mobilenetv2_coco_voctrainaug':
		'deeplabv3_mnv2_pascal_train_aug_2018_01_29.tar.gz',
	'mobilenetv2_coco_voctrainval':
		'deeplabv3_mnv2_pascal_trainval_2018_01_29.tar.gz',
	'xception_coco_voctrainaug':
		'deeplabv3_pascal_train_aug_2018_01_04.tar.gz',
	'xception_coco_voctrainval':
		'deeplabv3_pascal_trainval_2018_01_04.tar.gz',
}
_TARBALL_NAME = _MODEL_URLS[MODEL_NAME]

model_dir = 'deeplab_model'
if not os.path.exists(model_dir):
  tf.gfile.MakeDirs(model_dir)

download_path = os.path.join(model_dir, _TARBALL_NAME)
if not os.path.exists(download_path):
  print('downloading model to %s, this might take a while...' % download_path)
  urllib.request.urlretrieve(_DOWNLOAD_URL_PREFIX + _MODEL_URLS[MODEL_NAME], 
			     download_path)
  print('download completed! loading DeepLab model...')

model = DeepLabModel(download_path)

M_STR = ["height", "waist","belly", "chest", "wrist","neck","arm length","thigh","shoulder width","hips", "ankle"]

@app.hmr_app.route('/')
def index():
    return render_template('index.html')

@app.hmr_app.route('/infer', methods=['POST'])
def generate_object_file():

    user_id = request.form.get('user_id')

    if not user_id:
        return jsonify({'message': 'User id is required'})
    
    user = app.User.query.filter_by(id=user_id).first()
    print("here")
  #print all entries in the database
    for user in app.User.query.all():
        print(user.id)
        print("-----------------")

    if not user:
        return jsonify({'message': 'Invalid user id'})
    
    weight = user.weight
    height = user.height
    gender = user.gender

    image_file = request.form.get('image')
    measurements = model.get_dimensions(height, image_file)
    measurement_labels = ["height", "waist", "belly", "chest", "wrist", "neck", "arm length", "thigh", "shoulder width", "hips", "ankle", "weight", "gender"]
    formatted_measurements = {}
    formatted_measurements["weight"] = int(weight)
    formatted_measurements["gender"] = gender

    for label, value in zip(measurement_labels, measurements.tolist()):
        formatted_measurements[label] = value[0]
    
    requests.post('http://localhost:5001/generate', json=formatted_measurements)

    return jsonify(formatted_measurements)

if __name__ == '__main__':
    with app.hmr_app.app_context():
        app.db.create_all()
    
        print(app.db.engine.table_names())
    app.hmr_app.run(host='localhost', port=5002, debug=True)

