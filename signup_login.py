from flask import Flask, request, jsonify,  redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
#db.init_app(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
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
    image = db.Column(db.String(255))
    vendor = db.Column(db.String(150))
    vendor_link = db.Column(db.String(255))
    outfits = db.relationship('Outfit', secondary='outfit_item_association', backref='items', lazy='dynamic')

class Outfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # One-to-Many Relationship with User
    # Two items associated with each outfit: top and bottom
    top_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    bottom_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    top = db.relationship('Item', foreign_keys=[top_id], backref='outfit_top', uselist=False)
    bottom = db.relationship('Item', foreign_keys=[bottom_id], backref='outfit_bottom', uselist=False)

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))


outfit_item_association = db.Table('outfit_item_association',
    db.Column('outfit_id', db.Integer, db.ForeignKey('outfit.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
)

@app.route('/')
def index():
    return "Hello, World!"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#GET SIGNUP PAGE AND SIGNUP 
@app.route('/signup', methods=['POST'])
def signup():
    if request.method=='POST':

        data = request.get_json()
        # email = request.form['email']
        # password = request.form['password']
        # first_name = request.form['first_name']
        # weight = request.form['weight']
        # height = request.form['height']
        
        existing_user = User.query.filter_by(email=data['email']).first()
        # if existing_user:
        #     #flash('Email address already exists.')
        #     return redirect(url_for('signup'))
        if existing_user:
            return jsonify({'message': 'Email address already exists.'})
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        #hashed_password = generate_password_hash(password, method='sha256') # Hash the password before storing it
        
        new_user = User(email=data['email'], password=hashed_password, first_name=data['first_name'], weight = data['weight'], height = data['height']) # Create a new user
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'user_id': new_user.id})
        
        #flash('You have successfully signed up!')
        #return redirect(url_for('login'))

    

#GET USER
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id).first()
    return jsonify({'email': user.email, 'first_name': user.first_name, 'weight': user.weight, 'height': user.height})

#GET ALL ITEMS
@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    output = []
    for item in items:
        item_data = {'item_name': item.item_name, 'description': item.description, 'image': item.image, 'vendor': item.vendor, 'vendor_link': item.vendor_link}
        output.append(item_data)
    return jsonify({'items': output})

#GET ALL OUTFITS FOR A USER
@app.route('/outfits/<user_id>', methods=['GET'])
def get_outfits(user_id):
    outfits = Outfit.query.filter_by(user_id=user_id).all()
    output = []
    for outfit in outfits:
        outfit_data = {'name': outfit.name, 'top': outfit.top.item_name, 'bottom': outfit.bottom.item_name}
        output.append(outfit_data)
    return jsonify({'outfits': output})

#GET ITEM INFO
@app.route('/item/<item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    item_data = {'item_name': item.item_name, 'description': item.description, 'image': item.image, 'vendor': item.vendor, 'vendor_link': item.vendor_link}
    return jsonify({'item': item_data})

#USER POST LIKE
@app.route('/like', methods=['POST'])
def like_item():
    user_id = request.form['user_id']
    item_id = request.form['item_id']
    
    new_like = Likes(user_id=user_id, item_id=item_id)
    db.session.add(new_like)
    db.session.commit()
    
    return jsonify({'message': 'Item liked successfully'})

#EDIT USER INFO
@app.route('/edit', methods=['POST'])
def edit_user():
    user_id = request.form['user_id']
    user = User.query.filter_by(id=user_id).first()
    user.weight = request.form['weight']
    user.height = request.form['height']
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully'})

#ADD ITEM TO OUTFIT FROM USER
@app.route('/add_item', methods=['POST'])
def add_item():
    user_id = request.form['user_id']
    outfit_id = request.form['outfit_id']
    item_id = request.form['item_id']
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    user = User.query.filter_by(id=user_id).first()
    
    if outfit.user_id != user_id:
        return jsonify({'message': 'You do not have permission to add items to this outfit'})
    
    if len(outfit.items) == 2:
        return jsonify({'message': 'This outfit already has two items'})
    
    outfit.items.append(Item.query.filter_by(id=item_id).first())
    db.session.commit()
    
    return jsonify({'message': 'Item added to outfit successfully'})

#REMOVE ITEM FROM OUTFIT
@app.route('/remove_item', methods=['POST'])
def remove_item():
    user_id = request.form['user_id']
    outfit_id = request.form['outfit_id']
    item_id = request.form['item_id']
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    user = User.query.filter_by(id=user_id).first()
    
    if outfit.user_id != user_id:
        return jsonify({'message': 'You do not have permission to remove items from this outfit'})
    
    if len(outfit.items) == 0:
        return jsonify({'message': 'This outfit already has no items'})
    
    outfit.items.remove(Item.query.filter_by(id=item_id).first())
    db.session.commit()
    
    return jsonify({'message': 'Item removed from outfit successfully'})



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()

        # email = request.form['email']
        # password = request.form['password']
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            # Check password
            if bcrypt.check_password_hash(user.password, data['password']):
                #login_user(user)
                return jsonify({'message': 'Login successful', 'user_id': user.id})

                return redirect(url_for('dashboard'))
            else:
                return jsonify({'message': 'Invalid email or password.'})
                #flash('Invalid email or password.')
                return redirect(url_for('login'))
        
        #flash('Invalid email or password.')
        return redirect(url_for('login'))
    
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


engine = db.create_engine('sqlite:///example.db')

if __name__ == '__main__':
    # #close all sessions
    # db.session.close_all()
    # db.drop_all()
    with app.app_context():
        # db.drop_all()
        db.create_all() # Create tables for our models
    #db.create_all()
    app.run(debug=False)
    
