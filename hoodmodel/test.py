from flask import Flask, request, jsonify
import bpy

app = Flask(__name__)

# Define a route to execute Blender functionality
@app.route('/process_model', methods=['POST'])
def process_model():
    # Assuming the client sends data in JSON format
    data = request.json
    
    # Extract parameters from JSON data
    model_path = data.get('model_path')
    operation = data.get('operation')
    
    # Call your Blender script with the provided parameters
    result = blender_function(model_path, operation)
    
    # Return result to the client
    return jsonify(result)

import bpy

def blender_function(model_path, operation):
    # Import the model
    bpy.ops.import_scene.obj(filepath=model_path)
    
    # Get the imported object
    imported_object = bpy.context.scene.objects[-1]
    
    # Select the imported object
    bpy.context.view_layer.objects.active = imported_object
    
    # Add modifier
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 2
    
    # Apply modifier
    bpy.ops.object.modifier_apply(modifier="Subdivision")
    
    # Export the modified object
    bpy.ops.export_scene.obj(filepath="output.obj")

    return {'message': 'Model processed successfully'}


if __name__ == '__main__':
    app.run(debug=True)
