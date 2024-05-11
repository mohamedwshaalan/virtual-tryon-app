from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os 
db = SQLAlchemy()

#sanay

outfit_item_association = db.Table('outfit_item_association',
    db.Column('outfit_id', db.Integer, db.ForeignKey('outfit.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    outfits = db.relationship('Outfit', backref='user', lazy='dynamic')
    body_model = db.Column(db.LargeBinary)
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    gender = db.Column(db.String(150))


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
    item_link = db.Column(db.String(255))
    caption = db.Column(db.String(500))
    file_name = db.Column(db.String(255))

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

######################################################################################################

main_app = Flask(__name__, instance_relative_config=False)
main_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db' 
main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db.init_app(main_app)

mice_app = Flask(__name__, instance_relative_config=False)
mice_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
mice_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db.init_app(mice_app)

hmr_app = Flask(__name__, instance_relative_config=False)
hmr_app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///database.db'
hmr_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(hmr_app)

comprec_app = Flask(__name__, instance_relative_config=False)
comprec_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
comprec_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(comprec_app)

hood_app = Flask(__name__, instance_relative_config=False)
hood_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
hood_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(hood_app)

bpy_app = Flask(__name__, instance_relative_config=False)
bpy_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
bpy_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(bpy_app)

data_app = Flask(__name__, instance_relative_config=False)
data_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
data_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(data_app)

test_value = "shaalan"
