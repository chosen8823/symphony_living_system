from flask import Flask, request, jsonify
import os
import sys

# Add layers directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'layers'))

from drawing_interpreter import create_interpreter
from image_processor import create_processor, create_resonance_mapper

app = Flask(__name__)
AUTH_TOKEN = os.environ.get("SOPHIA_TOKEN", "divine-default")

# Initialize drawing analysis components
drawing_interpreter = create_interpreter()
image_processor = create_processor()
resonance_mapper = create_resonance_mapper()

@app.route("/sophia/read", methods=["POST"])
def sophia_read():
    data = request.json
    path = data.get("path")
    if not path or not os.path.isfile(path):
        return jsonify({"error": "Invalid path"}), 400
    with open(path, "r") as f:
        content = f.read()
    return jsonify({"content": content})

@app.route("/sophia/write", methods=["POST"])
def sophia_write():
    token = request.headers.get("Authorization", "")
    if token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    path = data.get("path")
    content = data.get("content")
    if not path or content is None:
        return jsonify({"error": "Missing path or content"}), 400
    with open(path, "w") as f:
        f.write(content)
    return jsonify({"status": "written", "path": path})

@app.route("/sophia/heartbeat")
def heartbeat():
    return jsonify({"status": "alive"})


@app.route("/sophia/interpret-drawing", methods=["POST"])
def interpret_drawing():
    """
    Analyze a drawing for sacred geometry and provide interpretation

    Expected JSON payload:
    {
        "image_path": "/path/to/image.png",  // OR
        "image_base64": "base64_encoded_string",
        "timestamp": "ISO-8601 timestamp",
        "user_context": {}  // optional metadata
    }
    """
    try:
        data = request.json

        # Load image from path or base64
        if "image_path" in data:
            image_data = image_processor.load_from_path(data["image_path"])
        elif "image_base64" in data:
            image_data = image_processor.load_from_base64(data["image_base64"])
        else:
            return jsonify({"error": "Must provide image_path or image_base64"}), 400

        # Check for errors in image loading
        if "error" in image_data:
            return jsonify({"error": image_data["error"]}), 400

        # Prepare drawing input for interpreter
        drawing_input = {
            "timestamp": data.get("timestamp"),
            "features": image_data.get("features", {}),
            "metadata": {
                "width": image_data.get("width"),
                "height": image_data.get("height"),
                "mode": image_data.get("mode")
            },
            "user_context": data.get("user_context", {})
        }

        # Perform interpretation
        interpretation = drawing_interpreter.interpret(drawing_input)

        # Add color resonance analysis if image array available
        if "array" in image_data:
            color_resonance = resonance_mapper.map_colors_to_frequencies(image_data["array"])
            interpretation["color_resonance"] = color_resonance

        return jsonify(interpretation)

    except Exception as e:
        return jsonify({"error": f"Interpretation failed: {str(e)}"}), 500


@app.route("/sophia/analyze-geometry", methods=["POST"])
def analyze_geometry():
    """
    Direct geometry analysis without full interpretation

    Expected JSON payload:
    {
        "features": {
            "circles": [...],
            "lines": [...],
            "vertices": [...],
            "spiral": {...}
        }
    }
    """
    try:
        data = request.json
        features = data.get("features", {})

        # Use the geometry analyzer directly
        results = drawing_interpreter.geometry_analyzer.analyze(features)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/sophia/extract-features", methods=["POST"])
def extract_features():
    """
    Extract geometric features from an image without interpretation

    Expected JSON payload:
    {
        "image_path": "/path/to/image.png",  // OR
        "image_base64": "base64_encoded_string"
    }
    """
    try:
        data = request.json

        # Load image
        if "image_path" in data:
            image_data = image_processor.load_from_path(data["image_path"])
        elif "image_base64" in data:
            image_data = image_processor.load_from_base64(data["image_base64"])
        else:
            return jsonify({"error": "Must provide image_path or image_base64"}), 400

        if "error" in image_data:
            return jsonify({"error": image_data["error"]}), 400

        # Return features only
        return jsonify({
            "features": image_data.get("features", {}),
            "metadata": {
                "width": image_data.get("width"),
                "height": image_data.get("height"),
                "mode": image_data.get("mode")
            }
        })

    except Exception as e:
        return jsonify({"error": f"Feature extraction failed: {str(e)}"}), 500


@app.route("/sophia/interpretation-history", methods=["GET"])
def get_interpretation_history():
    """
    Retrieve history of drawing interpretations
    """
    return jsonify({
        "count": len(drawing_interpreter.interpretation_history),
        "interpretations": drawing_interpreter.interpretation_history
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
