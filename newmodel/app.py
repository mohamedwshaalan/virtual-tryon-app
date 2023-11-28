from flask import Flask, request, render_template,  send_file
from test import Model  # Assuming model.py is in the same directory

app = Flask(__name__)
model = Model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_object_file():
    # look at test.py for the input data
    data = request.get_json()

    weight = data['weight']
    height = data['height']
    hips = data['hips']
    chest = data['chest']
    waist = data['waist']
    gender = data['gender'] 

    model.generate_object_file(weight, height, hips, chest,waist ,gender)

    return send_file("result.obj")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
