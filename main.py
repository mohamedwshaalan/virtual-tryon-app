from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


outfit_item_association = db.Table('outfit_item_association',
    db.Column('outfit_id', db.Integer, db.ForeignKey('outfit.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    outfits = db.relationship('Outfit', backref='user', lazy='dynamic')
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)

    def __repr__(self):
        return f'<User {self.username}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    garment_type_id = db.Column(db.Integer, db.ForeignKey('garment_type.id'), nullable=False)
    garment = db.relationship('GarmentType', backref=db.backref('items', lazy=True))
    front_image = db.Column(db.String(255))
    back_image = db.Column(db.String(255))
    texture = db.Column(db.String(255))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    outfits = db.relationship('Outfit', secondary='outfit_item_association', backref='items', lazy='dynamic')

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(150), nullable=False)
    vendor_link = db.Column(db.String(255))
    
class GarmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    garment_type = db.Column(db.String(150), nullable=False)
    object_file = db.Column(db.String(255))

class Outfit(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    top_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    bottom_id = db.Column(db.Integer, db.ForeignKey('item.id'))


@app.route('/')
def index():
    return "Hello, World!"

#Get certain item
@app.route('/item/<item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    item_data = {'id': item.id, 'item_name': item.item_name, 'description': item.description, 'front_image': item.front_image, 'back_image': item.back_image, 'texture': item.texture}
    return jsonify({'item': item_data})
    
#Get all items
@app.route('/item', methods=['GET'])
def get_items():
    items = Item.query.all()
    output = []
    for item in items:
        item_data = {'id': item.id, 'item_name': item.item_name, 'description': item.description, 'front_image': item.front_image, 'back_image': item.back_image, 'texture': item.texture}
        output.append(item_data)
    return jsonify({'items': output})

#Get likes for certain user
@app.route('/like/<user_id>', methods=['GET'])
def get_likes(user_id):
    #get email of user with this user email
    #user = User.query.filter_by(email=user_email).first()
    likes = Likes.query.filter_by(user_id=user_id)
    output = []
    for like in likes:
        item = Item.query.filter_by(id=like.item_id).first()
        if item is not None:
            item_data = {'id': item.id, 'item_name': item.item_name, 'description': item.description, 'front_image': item.front_image, 'back_image': item.back_image, 'texture': item.texture}
            output.append(item_data)
        else:
            print(f"Item with id {like.item_id} not found")  
    return jsonify({'likes': output})

#Get outfits for certain user
@app.route('/outfit/<user_id>', methods=['GET'])
def get_outfits(user_id):
    outfits = Outfit.query.filter_by(user_id=user_id)
    output = []
    for outfit in outfits:
        outfit_data = {'id': outfit.id, 'name': outfit.name, 'user_id': outfit.user_id, 'top_id': outfit.top_id, 'bottom_id': outfit.bottom_id}
        output.append(outfit_data)
    return jsonify({'outfits': output})

#post user like
@app.route('/like', methods=['POST'])
def like():
    data = request.get_json()
    new_like = Likes(user_id=data['user_id'], item_id=data['item_id'])
    db.session.add(new_like)
    db.session.commit()
    return jsonify({'message': 'New like created'})

#let user update their info
@app.route('/edit', methods=['POST'])
def edit():
    data = request.get_json()
    user = User.query.filter_by(id=data['user_id']).first()
    user.weight = data['weight']
    user.height = data['height']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

#let user add outfit without items
@app.route('/outfit', methods=['POST'])
def add_outfit():
    data = request.get_json()
    new_outfit = Outfit(name=data['name'], user_id=data['user_id'])
    db.session.add(new_outfit)
    db.session.commit()
    return jsonify({'message': 'Outfit added successfully'})

#let certain user add item to outfit
@app.route('/item', methods=['POST'])
def add_item():
    data = request.get_json()
    user = User.query.filter_by(id=data['user_id']).first()
    outfit = Outfit.query.filter_by(id=data['outfit_id']).first()
    if outfit.user_id != user.id:
        return jsonify({'message': 'User does not have permission to add item to outfit'})

    item = Item.query.filter_by(id=data['item_id']).first()
    if item.garment_type_id == 1:
        outfit.top_id = item.id
    elif item.garment_type_id == 2:
        outfit.bottom_id = item.id
    
    db.session.commit()
    return jsonify({'message': 'Item added to outfit successfully'})

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user_data = {'id': user.id, 'email': user.email, 'first_name': user.first_name, 'weight': user.weight, 'height': user.height}
    return jsonify({'user': user_data})

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 

    app.run(debug=True)