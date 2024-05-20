from flask import Flask, request, render_template,  send_file, jsonify
from mice import Model  # Assuming model.py is in the same directory
import os
import base64
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import app

model = Model()

@app.mice_app.route('/')
def index():
    return render_template('index.html')

@app.mice_app.route('/generate', methods=['POST'])
def generate_object_file():
   
    data = request.get_json()
    if 'user_id' not in data:
        return jsonify({'message': 'User id is required'})
    

    user = app.User.query.filter_by(id=data['user_id']).first()

    if not user:
        return jsonify({'message': 'Invalid user id'})

    weight = data['weight']
    height = data['height']
    hips = data['hips']
    chest = data['chest']
    waist = data['waist']
    gender = data['gender']

    model.generate_object_file(weight, height, hips, chest,waist ,gender)

    user.body_model = base64.b64encode(open('dump/body_model.obj', 'rb').read())

    user.weight = weight
    user.height = height
    user.gender = gender

    app.db.session.commit()
    return jsonify({'message': 'Body model generated successfully'})

if __name__ == '__main__':
    with app.mice_app.app_context():
        app.db.create_all()

    app.mice_app.run(host='localhost', port=5001, debug=True)
