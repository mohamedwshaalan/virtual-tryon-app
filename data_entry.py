import csv
import base64
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main

garment_type_mapping = {
    "Tshirt": 1,
    "Trouser": 2,
    "Polo": 3,
    "Shorts": 4,
    "Jacket": 5
}

# Function to encode image to base64
def encode_image(filename):
    path = filename + ".jpg" 
    with open(path, 'rb') as image_file:
        return base64.b64encode(image_file.read()) 

with main.app.app_context():
    with open('Database.csv', 'r', encoding = 'utf8') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            counter+= 1
            item_name, description, front_image_name, back_image_name, vendor_name, link, garment_type = row
            link = link.replace('\n', '')
            garment_type_id = garment_type_mapping.get(garment_type, 0)
            item = main.Item(item_name=item_name, description=description, garment_type_id=garment_type_id, front_image=encode_image(front_image_name), back_image=encode_image(back_image_name), texture=b'', vendor_id=1, item_link=link)
            main.db.session.add(item)   
            
    main.db.session.commit()


