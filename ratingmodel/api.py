import base64
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import random
import time
import os
import json
import sys
import torch
import re
from torchvision.transforms import ToTensor
sys.path.insert(0, "../mcn")
import torchvision.transforms as transforms
from model import CompatModel
from utils import prepare_dataloaders
from PIL import Image
from flask import Flask, request, render_template,  send_file
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import app

# Load the model
device = torch.device('cpu')
model = CompatModel(embed_size=1000, need_rep=True, vocabulary=2757).to(device)
model.load_state_dict(torch.load("/home/mahdy/Desktop/Backup/Application/virtual-tryon-app/ratingmodel/model2_train.pth", map_location="cpu"))
model.eval()
for name, param in model.named_parameters():
    if 'fc' not in name:
        param.requires_grad = False

def base64_to_tensor(image_bytes_dict):
    my_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    outfit_tensor = []
    for k, v in image_bytes_dict.items():
        img = base64_to_image(v)
        tensor = my_transforms(img)
        outfit_tensor.append(tensor.squeeze())
    outfit_tensor = torch.stack(outfit_tensor)
    outfit_tensor = outfit_tensor.to(device)
    return outfit_tensor

def defect_detect(img, model, normalize=True):
    relation = None

    def func_r(module, grad_in, grad_out):
        nonlocal relation
        relation = grad_in[1].detach()

    for name, module in model.named_modules():
        if name == 'predictor.0':
            module.register_backward_hook(func_r)
    
    out = model._compute_score(img)
    out = out[0]

    one_hot = torch.FloatTensor([[-1]]).to(device)
    model.zero_grad()
    out.backward(gradient=one_hot, retain_graph=True)

    if normalize:
        relation = relation / (relation.max() - relation.min())
    relation += 1e-3
    return relation, out.item()
def base64_to_image(base64_str):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = io.BytesIO(byte_data)
    img = Image.open(image_data).convert("RGB")
    return img


# def image_to_base64(image_key):
#     # Check if the image is included in the request
#     if image_key not in request.files:
#         return f"No image provided for key '{image_key}' in the request", 400
    
#     # Read the image from the request
#     image_file = request.files[image_key]
    
#     # Check if the file is an image
#     if image_file.filename == '':
#         return f"Empty filename for key '{image_key}'", 400
#     if not image_file.mimetype.startswith('image'):
#         return f"Uploaded file for key '{image_key}' is not an image", 400
    
#     # Convert the image to base64 string
#     image_bytes = image_file.read()
#     image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
#     return image_base64

def image_to_base64(image_file):
    image_data = image_file.read()
    base64_encoded_image = base64.b64encode(image_data).decode('utf-8')
    return base64_encoded_image

def image_path_to_base64(file_path):
    with open(file_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded_image = base64.b64encode(image_data).decode('utf-8')
    return base64_encoded_image

def inference(model, device, my_images):
    model = model.to(device)
    model.eval()
    transform = ToTensor()
    outputs = []
    with torch.no_grad():
        for img in my_images:
            # Apply transformations to the image
            img_tensor = transform(img).unsqueeze(0).to(device)
            # Pass the image through the model
            names = ["top", "bottom", "shoe", "bag"]
            output, _, _, _ = model(img_tensor, names)
            # Process the output as needed
            # For example, you can print the output
            outputs.append(output)
    
    
    return outputs

def convert_images_to_base64(request):
    base64_images = {}
    # for image_key in request.files:
    #     base64_image = image_to_base64(image_key)
    #     if isinstance(base64_image, tuple):
    #         return base64_image
    #     base64_images[image_key] = base64_image
    print('the image sent',request.files['bag'])
    base64_images['top'] = image_to_base64(request.files['top'])
    base64_images['bottom'] = image_to_base64(request.form.get('bottom'))
    base64_images['shoe'] = image_to_base64(request.form.get('shoe'))
    base64_images['bag'] = image_to_base64(request.form.get('bag'))
    base64_images['accessory'] = image_to_base64(request.form.get('accessory'))
    

    return base64_images

@app.rating_app.route('/predictrating', methods=['POST'])
def predict_rating():
    base64_images = {}
    
    #get ids for all the items from the body
    
    data = request.get_json()
    # top_id = data['top_id']


    base64_images['top'] = data['top']
    base64_images['bottom'] = data['bottom']
    # base64_images['shoe'] = image_to_base64(request.files['shoe'])
    # base64_images['bag'] = image_to_base64(request.files['bag'])
    # base64_images['accessory'] = image_to_base64(request.files['accessory'])

    base64_images['shoe'] = image_path_to_base64('shoe.jpeg')
    base64_images['bag'] = image_path_to_base64('bag2.png')
    base64_images['accessory'] = image_path_to_base64('necklace.jpg')


    # Convert the base64 images to tensors
    img_tensor = base64_to_tensor(base64_images)
    img_tensor.unsqueeze_(0)
    relation, score = defect_detect(img_tensor, model)
    outputs = {
        "score": score
    }
    return json.dumps(outputs)

if __name__ == '__main__':
    with app.rating_app.app_context():
        app.db.create_all()

    app.rating_app.run(host='localhost', port=5007, debug=True)