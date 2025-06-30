from flask import Flask, request, send_file, jsonify
import trimesh
import requests
import tempfile
from PIL import Image, ImageDraw
import numpy as np
import os

app = Flask(__name__)

@app.route("/render-stl", methods=["POST"])
def render_stl():
    data = request.get_json()
    file_url = data.get("fileUrl")

    if not file_url:
        return jsonify({"error": "Missing fileUrl"}), 400

    try:
        # Download STL
        response = requests.get(file_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            temp_file.write(response.content)
            stl_path = temp_file.name

        # Load mesh and project to 2D
        mesh = trimesh.load(stl_path)
        if mesh.is_empty:
            return jsonify({"error": "Failed to load STL"}), 400

        # Get 2D projection
        png = mesh.scene().save_image(resolution=(600, 600), visible=False)

        # Save final image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_img:
            out_img.write(png)
            return send_file(out_img.name, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
