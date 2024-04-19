# # from flask import Flask, request, jsonify
# # from image_model import ImageModel
# from flask import Flask, request, render_template 

# import sys
# sys.path.append('/app') 

# from model.testmodel import SimpleModel
# import os

# app = Flask(__name__)
# app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# model = SimpleModel()
# # model = ImageModel()

# @app.route('/')
# def home_page():
#     return "<p>Home Page<p>"

# @app.route('/user/<userid>')
# def user_page(userid):
#     return f"<p>User Page for user {userid}<p>"

# @app.route('/test')
# def index():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     input_value = float(request.form['input'])
#     prediction = model.predict(input_value)
#     return render_template('index.html', prediction=prediction)

# # if __name__ == '__main__':
# #     app.run(debug=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)

# # @app.route('/predict_image', methods=['POST'])
# # def getdimensions():
# #     # Get the uploaded image file from the request
# #     uploaded_file = request.files['file']

# #     # Save the image to a temporary location
# #     image_path = 'temp_image.jpg'
# #     uploaded_file.save(image_path)

# #     # Make a prediction using the model
# #     prediction = model.predict(image_path)

    
# #     return jsonify(prediction)
 # app/app.py
# app/app.py

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    input_value = float(request.form['input'])

    # Send a request to the model service
    model_url = 'http://model:5001/predict'  # Docker Compose service name as the hostname
    data = {'input': input_value}
    response = requests.post(model_url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        prediction = result['prediction']
        return render_template('index.html', prediction=prediction)
    else:
        return "Error communicating with the model service"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

