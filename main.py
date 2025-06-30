from flask import Flask, request, send_file, jsonify
import trimesh
import tempfile
import os

app = Flask(__name__)

@app.route("/render-stl", methods=["POST"])
def render_stl():
    if 'data' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['data']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            file.save(temp_file)
            temp_path = temp_file.name

        mesh = trimesh.load(temp_path)
        scene = mesh.scene()
        image = scene.save_image(resolution=(600, 600), visible=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_img:
            out_img.write(image)
            out_img_path = out_img.name

        return send_file(out_img_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
