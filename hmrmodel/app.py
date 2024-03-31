from flask import Flask, request, render_template
from inference import DeepLabModel
import os
import tensorflow as tf
from six.moves import urllib

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

#print("here")
app = Flask(__name__)
model = DeepLabModel(download_path)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/infer', methods=['POST'])
def generate_object_file():

    image_file = request.form.get('image')
    height = request.form.get('height')

    model.get_dimensions(height, image_file)

    return "done"


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)

