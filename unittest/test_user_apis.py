import unittest
from flask import Flask
from flask_testing import TestCase
from app import main_app, db, User, Item, Vendor, GarmentType, Outfit, Likes,  test_value
import main
import json

class MyTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True

    def create_app(self):
        main_app.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
        main_app.config['TESTING'] = self.TESTING
        return main_app

    def setUp(self):
        db.create_all()

        self.user = User(email="test@test.com", password="test", first_name="Test", weight=70, height=175, gender="male",
        body_model = b'')
        db.session.add(self.user)
        db.session.commit()

        self.vendor = Vendor(vendor_name="Test Vendor", vendor_link="http://testvendor.com")
        db.session.add(self.vendor)
        db.session.commit()

        self.item = Item(item_name="Test Item1", description="Test Description", garment_type_id=1,
         vendor_id=self.vendor.id, front_image = b'', back_image = b'', texture = b'', caption = "Test Caption")
        db.session.add(self.item)
        db.session.commit()

        self.outfit = Outfit(name="Test Outfit", user_id=self.user.id, top_id=self.item.id)
        db.session.add(self.outfit)
        db.session.commit()

        self.garment_type = GarmentType(garment_type="Test Garment Type")

    def tearDown(self):
        with main_app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_body(self):
        response = self.client.get(f'/body/{self.user.id}')
        self.assertEqual(response.status_code, 200)

    def test_fail_get_body_no_user(self):
        response = self.client.get(f'/body/100')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'] , 'Invalid user id')

    def test_fail_get_body_no_userid(self):
        response = self.client.get(f'/body/')
        self.assertEqual(response.status_code, 404)

 
    def test_get_item(self):
        response = self.client.get(f'/item/{self.item.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('item', response.json)

    def test_fail_get_item_no_item(self):
        response = self.client.get(f'/item/100')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'] , 'Invalid item id')
    
    def test_fail_get_item_no_itemid(self):
        response = self.client.get(f'/item/')
        self.assertEqual(response.status_code, 404)
        #self.assertEqual(response.json['message'] , 'No item id provided')
        
    def test_get_items(self):
        response = self.client.get(f'/item?user_id={self.user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('items', response.json)

    def test_fail_get_items_no_user(self):
        response = self.client.get(f'/item?user_id=100')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'] , 'Invalid user id')
    
    def test_fail_get_items_no_userid(self):
        response = self.client.get(f'/item?user_id=')
        self.assertEqual(response.json['message'] , 'No user id provided')
        self.assertEqual(response.status_code, 200)


    def test_get_likes(self):
        like = Likes(user_id=self.user.id, item_id=self.item.id)
        db.session.add(like)
        db.session.commit()

        response = self.client.get(f'/like/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('likes', response.json)

    def test_get_outfits(self):
        response = self.client.get(f'/outfit/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('outfits', response.json)

    def test_like(self):
        data = json.dumps({'user_id': self.user.id, 'item_id': self.item.id})
        response = self.client.post('/like', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_unlike(self):
        like = Likes(user_id=self.user.id, item_id=self.item.id)
        db.session.add(like)
        db.session.commit()

        data = json.dumps({'user_id': self.user.id, 'item_id': self.item.id})
        response = self.client.post('/unlike', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_edit(self):
        data = json.dumps({'user_id': self.user.id, 'weight': 75, 'height': 180, 'gender': 'female'})
        response = self.client.post('/edit', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_add_outfit(self):
        data = json.dumps({'user_id': self.user.id, 'item_id': self.item.id})
        response = self.client.post('/outfit', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_add_item(self):
        new_outfit = Outfit(name="New Outfit", user_id=self.user.id)
        db.session.add(new_outfit)
        db.session.commit()

        data = json.dumps({'user_id': self.user.id, 'outfit_id': new_outfit.id, 'item_id': self.item.id})
        response = self.client.post('/item', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_remove_item(self):
        data = json.dumps({'user_id': self.user.id, 'outfit_id': self.outfit.id, 'item_id': self.item.id})
        response = self.client.delete('/item', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_get_user(self):
        response = self.client.get(f'/user/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.json)



if __name__ == '__main__':
    unittest.main()
