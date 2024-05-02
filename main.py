from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import os
import base64

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


outfit_item_association = db.Table('outfit_item_association',
    db.Column('outfit_id', db.Integer, db.ForeignKey('outfit.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    outfits = db.relationship('Outfit', backref='user', lazy='dynamic')
    body_model = db.Column(db.LargeBinary)
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
    front_image = db.Column(db.LargeBinary)
    back_image = db.Column(db.LargeBinary)
    texture = db.Column(db.LargeBinary)
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
    object_file = db.Column(db.LargeBinary)

class Outfit(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    top_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    bottom_id = db.Column(db.Integer, db.ForeignKey('item.id'))


@app.route('/')
def index():
    return "Hello, World!"

#Get body of user
@app.route('/body/<user_id>', methods=['GET'])
def get_body(user_id): 
    user = User.query.filter_by(id=user_id).first()
    return jsonify({'body': base64.b64encode(user.body_model).decode('utf-8')})

#Get certain item
@app.route('/item/<item_id>', methods=['GET'])
def get_item(item_id):
    #get items front and back images and texture and decode them using base 64 then return
    item = Item.query.filter_by(id=item_id).first()
    #get vendor of this item
    vendor = Vendor.query.filter_by(id=item.vendor_id).first()
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
    
#Get all items
@app.route('/item', methods=['GET'])
def get_items():
    user_id = request.args.get('user_id')
    #print(user_id)
    if not user_id:
        return jsonify({'message': 'No user id provided'})

    user = User.query.filter_by(id=user_id).first()    
    if not user:
        return jsonify({'message': 'Invalid user id'})

    items = Item.query.all()
    output = []
    for item in items:
        vendor = Vendor.query.filter_by(id=item.vendor_id).first()
        like = Likes.query.filter_by(user_id=user.id, item_id=item.id).first()
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

#Get likes for certain user
@app.route('/like/<user_id>', methods=['GET'])
def get_likes(user_id):
    likes = Likes.query.filter_by(user_id=user_id)
    output = []
    for like in likes:
        item = Item.query.filter_by(id=like.item_id).first()
        vendor = Vendor.query.filter_by(id=item.vendor_id).first()
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
    like = Likes.query.filter_by(user_id=data['user_id'], item_id=data['item_id']).first()
    if like is not None:
        return jsonify({'message': 'User already liked this item'})
    new_like = Likes(user_id=data['user_id'], item_id=data['item_id'])
    db.session.add(new_like)
    db.session.commit()
    return jsonify({'message': 'New like created'})

#remove like from user
@app.route('/unlike', methods=['POST'])
def unlike():
    data = request.get_json()
    like = Likes.query.filter_by(user_id=data['user_id'], item_id=data['item_id']).first()
    db.session.delete(like)
    db.session.commit()
    return jsonify({'message': 'Like removed successfully'})

#let user update their info
@app.route('/edit', methods=['POST'])
def edit():
    data = request.get_json()
    user = User.query.filter_by(id=data['user_id']).first()
    user.weight = data['weight']
    user.height = data['height']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

#let user add outfit given an item
@app.route('/outfit', methods=['POST'])
def add_outfit():
    data = request.get_json()
    if 'user_id' not in data or 'item_id' not in data:
        return jsonify({'message': 'Name or user id not provided'})
    
    item = Item.query.filter_by(id=data['item_id']).first()
    if item is None: 
        return jsonify({'message': 'Item not found'})
    #if the item is a tshirt (1), or polo(2)or jacket(3) then it is a top else bottom
    if item.garment_type_id == 1 or item.garment_type_id == 2 or item.garment_type_id == 3:
        new_outfit = Outfit(name='Outfit' + str(data['user_id'])+ str(data['item_id']), user_id=data['user_id'], top_id=data['item_id'], bottom_id=None) 
    else:
        new_outfit = Outfit(name='Outfit' + str(data['user_id']) + str(data['item_id']), user_id=data['user_id'], top_id=data['item_id'], bottom_id=None)   

    db.session.add(new_outfit)
    db.session.commit()
    return jsonify({'message': 'Outfit added successfully'})

#let certain user add item to outfit
@app.route('/item', methods=['POST'])
def add_item():
    data = request.get_json()
    user = User.query.filter_by(id=data['user_id']).first()
    #check if user_id and outfit_id are sent in request
    if 'user_id' not in data or 'outfit_id' not in data:
        return jsonify({'message': 'User id or outfit id not provided'})
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

#let user remove item from outfit
@app.route('/item', methods=['DELETE'])
def remove_item():
    data = request.get_json()
    user = User.query.filter_by(id=data['user_id']).first()
    outfit = Outfit.query.filter_by(id=data['outfit_id']).first()
    if outfit.user_id != user.id:
        return jsonify({'message': 'User does not have permission to remove item from outfit'})

    item = Item.query.filter_by(id=data['item_id']).first()
    if item.garment_type_id == 1:
        outfit.top_id = None
    elif item.garment_type_id == 2:
        outfit.bottom_id = None
    
    # check if the outfit is empty
    if outfit.top_id is None and outfit.bottom_id is None:
        db.session.delete(outfit)
        

    db.session.commit()
    return jsonify({'message': 'Item removed from outfit successfully'})

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user_data = {'id': user.id, 'email': user.email, 'first_name': user.first_name, 'weight': user.weight, 'height': user.height}
    return jsonify({'user': user_data})

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#GET SIGNUP PAGE AND SIGNUP 
@app.route('/signup', methods=['POST'])
def signup():
    if request.method=='POST':

        data = request.get_json()
        
        existing_user = User.query.filter_by(email=data['email']).first()

        if existing_user:
            return jsonify({'message': 'Email address already exists.'})
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
        
        new_user = User(email=data['email'], password=hashed_password, first_name=data['first_name'], weight = data['weight'], height = data['height']) # Create a new user
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'user_id': new_user.id})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()

        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            # Check password
            if bcrypt.check_password_hash(user.password, data['password']):
                #login_user(user)
                return jsonify({'message': 'Login successful', 'user_id': user.id})

                return redirect(url_for('dashboard'))
            else:
                return jsonify({'message': 'Invalid email or password.'})

                return redirect(url_for('login'))
        
    
        return redirect(url_for('login'))
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 

    app.run(debug=True)

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