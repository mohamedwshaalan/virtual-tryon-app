from flask import Flask, request, render_template,  send_file, jsonify
from mice import Model  # Assuming model.py is in the same directory
import os
import base64
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


import main



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = '/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/instance/site.db'
model = Model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_object_file():
   
    data = request.get_json()

    user = main.db.User.query.filter_by(id=data['user_id']).first()
    if not user:
        return jsonify({'message': 'Invalid user id'})
    weight = user.weight
    height = user.height
    gender = 'female'

    hips = data['hips']
    chest = data['chest']
    waist = data['waist']

    body_model = model.generate_object_file(weight, height, hips, chest,waist ,gender)

    body_model = base64.b64encode(body_model.read()).decode('utf-8')

    user.body_model = body_model

    return jsonify({'message': 'Body model generated successfully'})

if __name__ == '__main__':
    with main.app.app_context():
        main.db.create_all()
    app.run(host='localhost', port=5001, debug=True)
