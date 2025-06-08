from flask import Flask, request, jsonify, Response
import os

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process_image() -> Response | tuple[Response, int]:
    """
    OCR server endpoint for processing images.

    Note: This server template requires OCR engine configuration.
    In production, inject the specific OCR implementation needed.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]
    if not image_file.filename:
        return jsonify({"error": "Invalid filename"}), 400

    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    image_path = os.path.join("uploads", image_file.filename)
    image_file.save(image_path)

    try:
        # OCR engine implementation should be injected here
        # For now, return a placeholder response
        return jsonify(
            {
                "grid": [["" for _ in range(10)] for _ in range(16)],
                "message": "OCR engine not configured",
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(image_path):
            os.remove(image_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8766)
