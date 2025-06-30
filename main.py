from flask import Flask, request, send_file, jsonify
import tempfile
import os
import trimesh
import PIL.Image
import io

app = Flask(__name__)

@app.route('/render-stl', methods=['POST'])
def render_stl():
    if 'data' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['data']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file.save(temp_file)
        temp_path = temp_file.name

    try:
        mesh = trimesh.load(temp_path, force='mesh')
        scene = mesh.scene()
        png_bytes = scene.save_image(resolution=(400, 400), visible=True)

        return send_file(
            io.BytesIO(png_bytes),
            mimetype='image/png',
            download_name='preview.png'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(temp_path)

if __name__ == '__main__':
    app.run(debug=True)
