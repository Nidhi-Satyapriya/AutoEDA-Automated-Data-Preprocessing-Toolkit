from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the AutoEDA Backend API!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    # Perform processing on the uploaded file here
    # For example, read the CSV into a DataFrame
    try:
        df = pd.read_csv(file)
        return jsonify({'message': 'File processed successfully!', 'data': df.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
