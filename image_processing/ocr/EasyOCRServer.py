# easyocr_server.py

from flask import Flask, request, jsonify
from EasyOCR import EasyOCR  # assuming your original class is saved in easyocr_module.py
import os

app = Flask(__name__)
ocr_engine = EasyOCR()

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image_path = os.path.join("uploads", image_file.filename)
    
    os.makedirs("uploads", exist_ok=True)
    image_file.save(image_path)
    
    try:
        ocr_reader = EasyOCR()
        ocr_list = ocr_reader.process_image(image_path)
        return jsonify(ocr_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=5000)
