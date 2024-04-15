from flask import Flask, request, jsonify,  redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

@app.route('/')
def index():
    return "Hello, World!"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#GET SIGNUP PAGE AND SIGNUP 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        weight = request.form['weight']
        height = request.form['height']
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists.')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password, method='sha256') # Hash the password before storing it
        
        new_user = User(email=email, password=hashed_password, first_name=first_name, weight = weight, height = height) # Create a new user
        db.session.add(new_user)
        db.session.commit()
        
        flash('You have successfully signed up!')
        return redirect(url_for('login'))

    return render_template('signup.html')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Check password
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('dashboard'))
        
        flash('Invalid email or password.')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)