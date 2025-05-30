from flask import Flask, request, jsonify
from vision.ocr.wrapper import EasyOCR
import os

app = Flask(__name__)
ocr_engine = EasyOCR()


@app.route("/process-image", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]
    if not image_file.filename:
        return jsonify({"error": "Invalid filename"}), 400

    image_path = os.path.join("uploads", image_file.filename)

    os.makedirs("uploads", exist_ok=True)
    image_file.save(image_path)

    try:
        ocr_list = ocr_engine.process_image(image_path)
        return jsonify(ocr_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
