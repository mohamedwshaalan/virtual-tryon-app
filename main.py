from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import os
import base64
import sys

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
        'texture': item.texture.decode('utf-8'), 
        'vendor_name': vendor.vendor_name, 
        'vendor_link' : vendor.vendor_link
    }
    return jsonify({'item': item_data})
    
#GET ALL ITEMS
@app.main_app.route('/item', methods=['GET'])
def get_items():
    
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'No user id provided'})

    user = app.User.query.filter_by(id=user_id).first()    
    if not user:
        return jsonify({'message': 'Invalid user id'})

    items = app.Item.query.all()
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
                'liked': True,
                'garment_type': 'top' if item.garment_type_id == 1 or item.garment_type_id  == 2 or item.garment_type_id == 3 else 'bottom'
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
                'garment_type': 'top' if item.garment_type_id == 1 or item.garment_type_id  == 2 or item.garment_type_id == 3 else 'bottom'
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
                'texture': item.texture.decode('utf-8'),
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
    #if the item is a tshirt (1), or polo(2) or jacket(3) then it is a top else bottom
    if item.garment_type_id == 1 or item.garment_type_id == 2 or item.garment_type_id == 3:
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
    if item.garment_type_id == 1 or item.garment_type_id == 2 or item.garment_type_id == 3:
        outfit.top_id = item.id
    elif item.garment_type_id == 4 or item.garment_type_id == 5:
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
    if item.garment_type_id == 1 or item.garment_type_id == 2 or item.garment_type_id == 3:
        outfit.top_id = None
    elif item.garment_type_id == 4 or item.garment_type_id == 5:
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
    

@app.main_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.main_app.app_context():
        app.db.create_all() 

        garment1 = app.GarmentType(garment_type='top', 
                                   object_file=base64.b64encode(open('/home/mahdy/Desktop/resized_garments/T-shirt/medium_tall.obj', 'rb').read()))
        garment2 = app.GarmentType(garment_type='bottom',
                                    object_file=base64.b64encode(open('/home/mahdy/Desktop/resized_garments/Pants/Medium_Tall.obj', 'rb').read()))
            
        app.db.session.add(garment1)
        app.db.session.add(garment2)
        app.db.session.commit()

        # garment1 = app.GarmentType(garment_type='top', object_file=b'')
        # garment2 = app.GarmentType(garment_type='bottom', object_file=b'')
        # app.db.session.add(garment1)
        # app.db.session.add(garment2)
        # app.db.session.commit()

        # # # #create vendors
        # vendor1 = app.Vendor(vendor_name='Zara', vendor_link='https://www.zara.com')
        # vendor2 = app.Vendor(vendor_name='H&M', vendor_link='https://www.hm.com')
        # app.db.session.add(vendor1)
        # app.db.session.add(vendor2)
        # app.db.session.commit()

        # # # create an item with the image encoded not the path
        # #open the image file 
        # image = open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/front5.jpeg', 'rb')

        # item1 = app.Item(item_name='Salma Shirt', description='A blue shirt', garment_type_id=1, 
        #             front_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/front5.jpeg', 'rb').read()),
        #             back_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/back5.jpeg', 'rb').read()), texture=b'', vendor_id=1)
        # item2 = app.Item(item_name='Salma Pants', description='Black pants', garment_type_id=2, 
        #             front_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/front19.jpeg', 'rb').read()),
        #             back_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/back19.jpeg', 'rb').read()), texture=b'', vendor_id=2)
        # app.db.session.add(item1)
        # app.db.session.add(item2)
        # app.db.session.commit()

        # # #create users
        # user1 = app.User(email = 'email 1', password = 'password 1', first_name = 'first name 1', body_model=b'', weight=150, height=70)
        # user2 = app.User(email = 'email 2', password = 'password 2', first_name = 'first name 2', body_model=b'', weight=160, height=72)
        # app.db.session.add(user1)
        # app.db.session.add(user2)
        # app.db.session.commit()

        # # # #create outfits
        # outfit1 = app.Outfit(name='Outfit 1', user_id=1)
        # outfit2 = app.Outfit(name='Outfit 2', user_id=2)
        # app.db.session.add(outfit1)
        # app.db.session.add(outfit2)

        # # # #add items to outfits
        # outfit1.items.append(item1)
        # outfit2.items.append(item2)
        # app.db.session.commit()

    app.main_app.run(debug=True)

#populate the db with datafromthefolder
# Get the path to the folder containing the obj files
# obj_folder = '/home/mahdy/Desktop/virtual_tryon_app_main/Garment Meshes-20240429T133228Z-001/Garment Meshes'

# # Iterate over the files in the folder
# for filename in os.listdir(obj_folder):
#     if filename.endswith('.obj'):
#         # Read the obj file


#         obj_data=base64.b64encode(open(os.path.join(obj_folder, filename), 'rb').read())
#         # Process the obj data and create a new GarmentType object
#         garment_type = GarmentType(garment_type=filename[:-4], object_file=obj_data)

#         # Add the garment type to the database
#         db.session.add(garment_type)

# Commit the changes to the database
#db.session.commit()
# # # #populate the db with some data
# # # #create garment types
# garment1 = GarmentType(garment_type='top', object_file=b'')
# garment2 = GarmentType(garment_type='bottom', object_file=b'')
# db.session.add(garment1)
# db.session.add(garment2)
# db.session.commit()

# # # #create vendors
# vendor1 = Vendor(vendor_name='Zara', vendor_link='https://www.zara.com')
# vendor2 = Vendor(vendor_name='H&M', vendor_link='https://www.hm.com')
# db.session.add(vendor1)
# db.session.add(vendor2)
# db.session.commit()

# # # create an item with the image encoded not the path
# #open the image file 
# image = open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/front5.jpeg', 'rb')

# item1 = Item(item_name='Salma Shirt', description='A blue shirt', garment_type_id=1, 
#              front_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/front5.jpeg', 'rb').read()),
#                back_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/back5.jpeg', 'rb').read()), texture=b'', vendor_id=1)
# item2 = Item(item_name='Salma Pants', description='Black pants', garment_type_id=2, 
#              front_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/front19.jpeg', 'rb').read()),
#               back_image=base64.b64encode(open('/home/mahdy/Desktop/Thesis-Flutter-Frontend/assets/images/clothing/back19.jpeg', 'rb').read()), texture=b'', vendor_id=2)
# db.session.add(item1)
# db.session.add(item2)
# db.session.commit()

# # #create users
# user1 = User(email = 'email 1', password = 'password 1', first_name = 'first name 1', body_model=b'', weight=150, height=70)
# user2 = User(email = 'email 2', password = 'password 2', first_name = 'first name 2', body_model=b'', weight=160, height=72)
# db.session.add(user1)
# db.session.add(user2)
# db.session.commit()

# # # #create outfits
# outfit1 = Outfit(name='Outfit 1', user_id=1)
# outfit2 = Outfit(name='Outfit 2', user_id=2)
# db.session.add(outfit1)
# db.session.add(outfit2)

# # # #add items to outfits
# outfit1.items.append(item1)
# outfit2.items.append(item2)
# db.session.commit()