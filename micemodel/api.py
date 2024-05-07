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

    user = app.User.query.filter_by(id=data['user_id']).first()

    if not user:
        return jsonify({'message': 'Invalid user id'})
    weight = user.weight
    height = user.height
    gender = user.gender

    hips = data['hips']
    chest = data['chest']
    waist = data['waist']

    model.generate_object_file(weight, height, hips, chest,waist ,gender)
    
    #body_model = open("dump/body_model.obj", 'rb')


    user.body_model = base64.b64encode(open('dump/body_model.obj', 'rb').read())

    app.db.session.commit()


    # os.remove("dump/body_model.obj")

    return jsonify({'message': 'Body model generated successfully'})

if __name__ == '__main__':
    with app.mice_app.app_context():
        app.db.create_all()

        # user = app.User(email = 'email 1', password = 'password 1', first_name = 'first name 1', body_model=b'', weight= 70, height = 180, gender = 'male')
        # app.db.session.add(user)
        # app.db.session.commit()

                    

    app.mice_app.run(host='localhost', port=5001, debug=True)
