from flask import Flask, request, jsonify, send_file
import trimesh
import tempfile
import os
import traceback

app = Flask(__name__)

@app.route("/render-stl", methods=["POST"])
def render_stl():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        ext = os.path.splitext(uploaded_file.filename)[1].lower()
        if ext not in [".stl", ".obj"]:
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            uploaded_file.save(temp_file)
            temp_path = temp_file.name

        # Load the mesh
        mesh = trimesh.load(temp_path, force='mesh')

        if mesh.is_empty:
            return jsonify({"error": "Failed to load mesh"}), 400

        scene = mesh.scene()
        image = scene.save_image(resolution=(600, 600), visible=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_img:
            out_img.write(image)
            out_img_path = out_img.name

        return send_file(out_img_path, mimetype='image/png')

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

# Needed for Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
