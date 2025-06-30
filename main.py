import os
import io
import tempfile
import trimesh # type: ignore
import pyrender # type: ignore
import numpy as np # type: ignore
from PIL import Image # type: ignore
from flask import Flask, request, send_file, jsonify # type: ignore

app = Flask(__name__)

@app.route('/render-stl', methods=['POST'])
def render_stl():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file.save(temp_file)
        temp_path = temp_file.name

    try:
        # Load mesh
        mesh = trimesh.load(temp_path, force='mesh')
        if not isinstance(mesh, trimesh.Trimesh):
            mesh = mesh.dump().sum()  # flatten scene if it's a scene

        # Convert to pyrender mesh
        render_mesh = pyrender.Mesh.from_trimesh(mesh)

        # Set up scene and renderer
        scene = pyrender.Scene()
        scene.add(render_mesh)

        renderer = pyrender.OffscreenRenderer(viewport_width=600, viewport_height=600)
        color, _ = renderer.render(scene)
        renderer.delete()

        # Convert to image and return
        image = Image.fromarray(color)
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='preview.png')

    except Exception as e:
        app.logger.error(f"Error processing file: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
