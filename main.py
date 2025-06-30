from flask import Flask, request, send_file, jsonify
import tempfile
import os
import requests
import numpy as np
import trimesh
import pyrender
from PIL import Image

app = Flask(__name__)

@app.route('/render-stl', methods=['POST'])
def render_stl():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        mesh = trimesh.load(temp_path)
        scene = pyrender.Scene()
        mesh = pyrender.Mesh.from_trimesh(mesh)
        scene.add(mesh)

        camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
        scene.add(camera, pose=[[1, 0, 0, 0],
                                [0, 1, 0, -0.1],
                                [0, 0, 1, 0.3],
                                [0, 0, 0, 1]])

        light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
        scene.add(light, pose=[[1, 0, 0, 0],
                               [0, 1, 0, 0],
                               [0, 0, 1, 1],
                               [0, 0, 0, 1]])

        renderer = pyrender.OffscreenRenderer(512, 512)
        color, _ = renderer.render(scene)
        image = Image.fromarray(color)

        output_path = temp_path.replace(".stl", "_preview.png")
        image.save(output_path)

        return send_file(output_path, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(output_path):
            os.remove(output_path)
