from flask import Flask, request, jsonify, redirect, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import base64
import sys
import pandas as pd
import app


bcrypt = Bcrypt(app.main_app)

login_manager = LoginManager()
login_manager.init_app(app.main_app)
login_manager.login_view = 'login'

@app.main_app.route('/')
def index():
    return "Hello, World!"

#GET BODY OF USER
@app.main_app.route('/body/<user_id>', methods=['GET'])
def get_body(user_id): 

    user = app.User.query.filter_by(id=user_id).first()
    return jsonify({'body': user.body_model.decode('utf-8')})

#GET ITEM
@app.main_app.route('/item/<item_id>', methods=['GET'])
def get_item(item_id):

    item = app.Item.query.filter_by(id=item_id).first()

    vendor = app.Vendor.query.filter_by(id=item.vendor_id).first()
    item_data = { 
        'id': item.id, 
        'item_name': item.item_name, 
        'description': item.description, 
        'front_image': item.front_image.decode('utf-8'),  
        'back_image': item.back_image.decode('utf-8'), 
        'texture':item.texture.decode('utf-8') if ((item.texture is None) or (item.texture==b''))  else item.texture, 
        'vendor_name': vendor.vendor_name, 
        'vendor_link' : vendor.vendor_link
    }
    return jsonify({'item': item_data})
    
#GET ITEMS   
@app.main_app.route('/item', methods=['GET'])
def get_items():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'No user id provided'})

    user = app.User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': 'Invalid user id'})

    items = app.Item.query.limit(200).all()

    output = []
    for item in items:
        vendor = app.Vendor.query.filter_by(id=item.vendor_id).first()
        like = app.Likes.query.filter_by(user_id=user.id, item_id=item.id).first()
        if like is not None:
            item_data = {
                'id': item.id,
                'item_name': item.item_name,
                'description': item.description,
                'front_image': item.front_image.decode('utf-8'),
                'back_image': item.back_image.decode('utf-8'),
                'texture': item.texture.decode('utf-8'),
                'vendor': vendor.vendor_name,
                'vendor_link': vendor.vendor_link,
                'item_link': item.item_link,
                'liked': True,
                'garment_type': 'top' if item.garment_type_id in (1, 3, 5) else 'bottom'
           }

        else:
            item_data = {
                'id': item.id,
                'item_name': item.item_name,
                'description': item.description,
                'front_image': item.front_image.decode('utf-8'),
                'back_image': item.back_image.decode('utf-8'),
                'texture': item.texture.decode('utf-8'),
                'vendor': vendor.vendor_name,
                'vendor_link': vendor.vendor_link,
                'liked': False,
                'garment_type': 'top' if item.garment_type_id in (1, 3, 5) else 'bottom'
            }
        output.append(item_data)
    return jsonify({'items': output})

#GET LIKES FOR USER
@app.main_app.route('/like/<user_id>', methods=['GET'])
def get_likes(user_id):
    likes = app.Likes.query.filter_by(user_id=user_id)
    output = []
    for like in likes:
        item = app.Item.query.filter_by(id=like.item_id).first()
        vendor = app.Vendor.query.filter_by(id=item.vendor_id).first()
        if item is not None:
            item_data = {
                'id': item.id, 
                'item_name': item.item_name, 
                'description': item.description, 
                'front_image': item.front_image.decode('utf-8'), 
                'back_image': item.back_image.decode('utf-8'), 
                'texture': item.texture.decode('utf-8') if ((item.texture is None) or (item.texture==b''))  else item.texture,
                'vendor': vendor.vendor_name,
                'vendor_link': vendor.vendor_link}
            output.append(item_data)
        else:
            print(f"Item with id {like.item_id} not found")  
    return jsonify({'likes': output})

#GET OUTFITS FOR USER
@app.main_app.route('/outfit/<user_id>', methods=['GET'])
def get_outfits(user_id):
    outfits = app.Outfit.query.filter_by(user_id=user_id)
    output = []
    for outfit in outfits:
        outfit_data = {'id': outfit.id, 'name': outfit.name, 'user_id': outfit.user_id, 'top_id': outfit.top_id, 'bottom_id': outfit.bottom_id}
        output.append(outfit_data)

    return jsonify({'outfits': output})

#POST LIKE FOR USER
@app.main_app.route('/like', methods=['POST'])
def like():
    data = request.get_json()
    like = app.Likes.query.filter_by(user_id=data['user_id'], item_id=data['item_id']).first()
    if like is not None:
        return jsonify({'message': 'User already liked this item'})
    new_like = app.Likes(user_id=data['user_id'], item_id=data['item_id'])
    app.db.session.add(new_like)
    app.db.session.commit()
    return jsonify({'message': 'New like created'})

#DELETE LIKE FOR USER
@app.main_app.route('/unlike', methods=['POST'])
def unlike():
    data = request.get_json()
    like = app.Likes.query.filter_by(user_id=data['user_id'], item_id=data['item_id']).first()
    app.db.session.delete(like)
    app.db.session.commit()
    return jsonify({'message': 'Like removed successfully'})

#UPDATE USER INFO
@app.main_app.route('/edit', methods=['POST'])
def edit():
    data = request.get_json()
    user = app.User.query.filter_by(id=data['user_id']).first()
    user.weight = data['weight']
    user.height = data['height']
    user.gender = data['gender']
    
    app.db.session.commit()
    return jsonify({'message': 'User updated successfully'})

#POST OUTFIT WITH ITEM FOR USER
@app.main_app.route('/outfit', methods=['POST'])
def add_outfit():
    data = request.get_json()
    if 'user_id' not in data or 'item_id' not in data:
        return jsonify({'message': 'Name or user id not provided'})
    
    item = app.Item.query.filter_by(id=data['item_id']).first()
    if item is None: 
        return jsonify({'message': 'Item not found'})
    #if the item is a tshirt (1), or polo(3) or jacket(5) then it is a top else bottom
    if item.garment_type_id == 1 or item.garment_type_id == 3 or item.garment_type_id == 5:
        new_outfit = app.Outfit(name='Outfit' + str(data['user_id'])+ str(data['item_id']), user_id=data['user_id'], top_id=data['item_id'], bottom_id=None) 
    else:
        new_outfit = app.Outfit(name='Outfit' + str(data['user_id']) + str(data['item_id']), user_id=data['user_id'], top_id=None, bottom_id=data['item_id'])   

    app.db.session.add(new_outfit)
    app.db.session.commit()
    return jsonify({'message': 'Outfit added successfully'})

#POST ITEM TO OUTFIT FOR USER
@app.main_app.route('/item', methods=['POST'])
def add_item():
    data = request.get_json()
    user = app.User.query.filter_by(id=data['user_id']).first()
    if 'user_id' not in data or 'outfit_id' not in data:
        return jsonify({'message': 'User id or outfit id not provided'})
    outfit = app.Outfit.query.filter_by(id=data['outfit_id']).first()
    if outfit.user_id != user.id:
        return jsonify({'message': 'User does not have permission to add item to outfit'})

    item = app.Item.query.filter_by(id=data['item_id']).first()
    if item.garment_type_id == 1 or item.garment_type_id == 3 or item.garment_type_id == 5:
        outfit.top_id = item.id
    elif item.garment_type_id == 2 or item.garment_type_id == 4:
        outfit.bottom_id = item.id
    
    app.db.session.commit()
    return jsonify({'message': 'Item added to outfit successfully'})

#DELETE ITEM FROM OUTFIT FOR USER
@app.main_app.route('/item', methods=['DELETE'])
def remove_item():
    data = request.get_json()
    user = app.User.query.filter_by(id=data['user_id']).first()
    outfit = app.Outfit.query.filter_by(id=data['outfit_id']).first()
    if outfit.user_id != user.id:
        return jsonify({'message': 'User does not have permission to remove item from outfit'})

    item = app.Item.query.filter_by(id=data['item_id']).first()
    if item.garment_type_id == 1 or item.garment_type_id == 3 or item.garment_type_id == 5:
        outfit.top_id = None
    elif item.garment_type_id == 2 or item.garment_type_id == 4:
        outfit.bottom_id = None
    
    if outfit.top_id is None and outfit.bottom_id is None:
        app.db.session.delete(outfit)
        

    app.db.session.commit()
    return jsonify({'message': 'Item removed from outfit successfully'})

#GET USER
@app.main_app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = app.User.query.filter_by(id=user_id).first()
    user_data = {'id': user.id, 'email': user.email, 'first_name': user.first_name, 'weight': user.weight, 'height': user.height, 'gender' : user.gender}
    return jsonify({'user': user_data})

@login_manager.user_loader
def load_user(user_id):
    return app.User.query.get(int(user_id))

#SIGNUP
@app.main_app.route('/signup', methods=['POST'])
def signup():
    if request.method=='POST':

        data = request.get_json()
        
        existing_user = app.User.query.filter_by(email=data['email']).first()

        if existing_user:
            return jsonify({'message': 'Email address already exists.'})
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
        
        new_user = app.User(email=data['email'], password=hashed_password, first_name=data['first_name'], weight = data['weight'], height = data['height'], gender=data['gender']) # Create a new user
        app.db.session.add(new_user)
        print(new_user.id)
        app.db.session.commit()
        return jsonify({'message': 'User created successfully', 'user_id': new_user.id})

#LOGIN
@app.main_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()

        user = app.User.query.filter_by(email=data['email']).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, data['password']):
                return jsonify({'message': 'Login successful', 'user_id': user.id})

    
            else:
                return jsonify({'message': 'Invalid email or password.'})

        
    
        return redirect(url_for('login'))
    
#LOGOUT
@app.main_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#SEARCH FOR SIMILAR ITEMS
@app.main_app.route('/search', methods=['GET'])
def search():

    search_query = request.args.get('query')
    if not search_query:
        return jsonify({'message': 'No search query provided'})

    items = app.Item.query.all()

    item_ids = []
    item_captions = []
    for item in items:
        item_ids.append(item.id)
        item_captions.append(item.caption)
    df = pd.DataFrame({'item_id': item_ids, 'item_caption': item_captions})
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['item_caption'])
    target_tfidf = vectorizer.transform([search_query])
    similarities = cosine_similarity(target_tfidf, tfidf_matrix)

    num_similarities = 5
    top_indices = similarities.argsort()[0, :-num_similarities-1:-1]

    top_similarities = df.iloc[top_indices]

    top_ids = top_similarities['item_id'].tolist()

    output = []
    for item_id in top_ids:
        item = app.Item.query.filter_by(id=item_id).first()
        vendor = app.Vendor.query.filter_by(id=item.vendor_id).first()
        item_data = {
            'id': item.id, 
            'item_name': item.item_name, 
            'description': item.description, 
            'front_image': item.front_image.decode('utf-8'), 
            'back_image': item.back_image.decode('utf-8'), 
            'texture': item.texture.decode('utf-8') if ((item.texture is None) or (item.texture==b''))  else item.texture, 
            'vendor': vendor.vendor_name, 
            'vendor_link': vendor.vendor_link
        }
        output.append(item_data)
    return jsonify({'items': output})

if __name__ == '__main__':
    with app.main_app.app_context():
        app.db.create_all() 

    app.main_app.run(debug=True)

