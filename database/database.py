from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    outfits = db.relationship('Outfit', backref='user', lazy='dynamic')

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

    # One-to-Many Relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Two items associated with each outfit: top and bottom
    top_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    bottom_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    # Relationship Definitions
    top = db.relationship('Item', foreign_keys=[top_id], backref='outfit_top', uselist=False)
    bottom = db.relationship('Item', foreign_keys=[bottom_id], backref='outfit_bottom', uselist=False)

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists.')
            return redirect(url_for('signup'))
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='sha256')
        
        # Create a new user
        new_user = User(email=email, password=hashed_password, first_name=first_name)
        db.session.add(new_user)
        db.session.commit()
        
        flash('You have successfully signed up!')
        return redirect(url_for('login'))

    return render_template('signup.html')

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


@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
