from flask import Flask, request, jsonify, send_file
import requests
import tempfile
import os
import trimesh

app = Flask(__name__)

@app.route("/render-stl", methods=["POST"])
def render_stl():
    data = request.get_json()
    file_url = data.get("fileUrl")

    if not file_url:
        return jsonify({"error": "Missing fileUrl"}), 400

    try:
        response = requests.get(file_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        mesh = trimesh.load(tmp_path, force='mesh')

        # Render as image with offscreen software renderer
        image_data = mesh.scene().save_image(resolution=[512, 512], visible=True)

        # Save to temp PNG
        image_path = tmp_path.replace(".stl", "_preview.png")
        with open(image_path, "wb") as f:
            f.write(image_data)

        return send_file(image_path, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
