from flask import Flask, request, jsonify
from image_model import ImageModel


app = Flask(__name__)

model = ImageModel()

@app.route('/')
def home_page():
    return "<p>Home Page<p>"

@app.route('/user/<userid>')
def user_page(userid):
    return f"<p>User Page for user {userid}<p>"

@app.route('/predict_image', methods=['POST'])
def getdimensions():
    # Get the uploaded image file from the request
    uploaded_file = request.files['file']

    # Save the image to a temporary location
    image_path = 'temp_image.jpg'
    uploaded_file.save(image_path)

    # Make a prediction using the model
    prediction = model.predict(image_path)

    
    return jsonify(prediction)
 