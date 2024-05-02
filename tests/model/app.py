from flask import Flask, request, jsonify
from testmodel import SimpleModel  # Assuming model.py is in the same directory

app = Flask(__name__)
model = SimpleModel()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_value = data['input']
    prediction = model.predict(input_value)
    return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)