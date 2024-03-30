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


app = Flask(__name__)

# Load the model
device = torch.device('cuda:0')
model = CompatModel(embed_size=1000, need_rep=True, vocabulary=2757).to(device)


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

def base64_to_image(base64_str):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = io.BytesIO(byte_data)
    img = Image.open(image_data).convert("RGB")
    return img


def image_to_base64(image_key):
    # Check if the image is included in the request
    if image_key not in request.files:
        return f"No image provided for key '{image_key}' in the request", 400
    
    # Read the image from the request
    image_file = request.files[image_key]
    
    # Check if the file is an image
    if image_file.filename == '':
        return f"Empty filename for key '{image_key}'", 400
    if not image_file.mimetype.startswith('image'):
        return f"Uploaded file for key '{image_key}' is not an image", 400
    
    # Convert the image to base64 string
    image_bytes = image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    return image_base64


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
    for image_key in request.files:
        base64_image = image_to_base64(image_key)
        if isinstance(base64_image, tuple):
            return base64_image
        base64_images[image_key] = base64_image
    return base64_images

@app.route('/predictrating', methods=['POST'])
def predict_rating():
    # Get the base64 images from the request
    base64_images_dict = convert_images_to_base64(request)
    top_img=request['top']
    bottom_img=request['bottom']
    shoe_img=request['shoe']
    bag_img=request['bag']
    accessory_img=request['accessory']

    # Convert the base64 images to tensors
    img_tensor = base64_to_tensor(base64_images_dict)
    img_tensor.unsqueeze_(0)
    # Perform inference
    outputs = inference(model, device, [top_img, bottom_img, shoe_img, bag_img, accessory_img])
    
    return json.dumps(outputs)