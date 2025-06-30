import os
import io
import tempfile
import trimesh
import plotly.graph_objects as go
from PIL import Image
from flask import Flask, request, send_file, jsonify

print("🚀 Flask app is starting...")

app = Flask(__name__)

# Health check route
@app.route('/', methods=['GET'])
def health_check():
    return 'App is running!', 200

@app.route('/render-stl', methods=['POST'])
def render_stl():
    if 'file' not in request.files:
        app.logger.error("❌ No file uploaded.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("❌ File selected, but no filename.")
        return jsonify({"error": "No file selected"}), 400

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file.save(temp_file)
        temp_path = temp_file.name

    try:
        mesh = trimesh.load(temp_path, force='mesh')

        if mesh.vertices.size == 0 or mesh.faces.size == 0:
            app.logger.error("❌ STL has no mesh data.")
            return jsonify({"error": "No mesh data found in STL file."}), 400

        fig = go.Figure(data=[
            go.Mesh3d(
                x=mesh.vertices[:, 0],
                y=mesh.vertices[:, 1],
                z=mesh.vertices[:, 2],
                i=mesh.faces[:, 0],
                j=mesh.faces[:, 1],
                k=mesh.faces[:, 2],
                color='lightblue',
                opacity=0.7
            )
        ])

        fig.update_layout(
            scene_camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            ),
            margin=dict(l=0, r=0, b=0, t=0),
        )

        app.logger.info("✅ Rendering image...")
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        fig.write_image(temp_img.name, width=600, height=600, scale=1)
        temp_img.seek(0)

        return send_file(temp_img.name, mimetype='image/png', as_attachment=True, download_name='preview.png')

    except Exception as e:
        app.logger.error(f"❌ Preview generation failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
