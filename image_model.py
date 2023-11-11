from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np

class ImageModel:
    def __init__(self):
        # Load the MobileNetV2 model pre-trained on ImageNet data
        self.model = MobileNetV2(weights='imagenet')

    def predict(self, image_path):
        # Load and preprocess the input image
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Make a prediction using the model
        predictions = self.model.predict(img_array)

        # Decode predictions (get human-readable labels)
        decoded_predictions = decode_predictions(predictions, top=1)[0]

        # Extract the class label and confidence score
        label = decoded_predictions[0][1]
        confidence = float(decoded_predictions[0][2])

        return {'label': label, 'confidence': confidence}
