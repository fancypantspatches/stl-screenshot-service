import os
import io
import tempfile
import trimesh
import plotly.graph_objects as go
from PIL import Image
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

@app.route('/render-stl', methods=['POST'])
def render_stl():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file.save(temp_file)
        temp_path = temp_file.name

    try:
        mesh = trimesh.load(temp_path, force='mesh')

        fig = go.Figure(data=[
            go.Mesh3d(
                x=mesh.vertices[:, 0],
                y=mesh.vertices[:, 1],
                z=mesh.vertices[:, 2],
                i=mesh.faces[:, 0],
                j=mesh.faces[:, 1],
                k=mesh.faces[:, 2],
                color='lightblue',
                opacity=0.5
            )
        ])
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            ),
            margin=dict(l=0, r=0, b=0, t=0),
        )

        # Save to a temporary image
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        fig.write_image(temp_img.name, width=600, height=600, scale=1)
        temp_img.seek(0)

        return send_file(temp_img.name, mimetype='image/png', as_attachment=True, download_name='preview.png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        os.remove(temp_path)
