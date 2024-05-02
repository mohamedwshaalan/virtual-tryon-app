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
    
        db.create_all() # Create tables for our models
  
    app.run(debug=False)
    
