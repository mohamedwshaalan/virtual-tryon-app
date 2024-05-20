import base64

jacket_obj = open('/home/mahdy/Desktop/resized_garments/jacket/jacket_aligned.obj', 'rb').read()
jacket_obj = base64.b64encode(jacket_obj)
print(jacket_obj)
with open('encoded_object.txt', 'w') as file:
    file.write(jacket_obj.decode('utf-8'))