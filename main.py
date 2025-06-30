from flask import Flask, request, send_file, jsonify
import tempfile
import os
import requests
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

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

        # Create plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        mesh_faces = mesh.vertices[mesh.faces]
        ax.add_collection3d(Poly3DCollection(mesh_faces, facecolor='lightgrey', edgecolor='black', linewidths=0.1, alpha=1))

        scale = mesh.vertices.flatten()
        ax.auto_scale_xyz(scale, scale, scale)
        ax.axis('off')

        preview_path = temp_path.replace(".stl", "_preview.png")
        plt.savefig(preview_path, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()

        return send_file(preview_path, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(preview_path):
            os.remove(preview_path)
