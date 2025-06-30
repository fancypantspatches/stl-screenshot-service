from flask import Flask, request, jsonify, send_file
import trimesh
import requests
import tempfile
import os

app = Flask(__name__)

@app.route("/render-stl", methods=["POST"])
def render_stl():
    data = request.get_json()
    file_url = data.get("fileUrl")

    if not file_url:
        return jsonify({"error": "Missing fileUrl"}), 400

    try:
        # Download the STL file
        response = requests.get(file_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name

        # Load the STL with trimesh
        mesh = trimesh.load(temp_path)

        # Create an image using scene
        scene = mesh.scene()
        image = scene.save_image(resolution=(600, 600), visible=True)

        # Save to another temp file as PNG
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_img:
            out_img.write(image)
            out_img_path = out_img.name

        return send_file(out_img_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

