# main.py
# This Flask application is designed to be called by an automated workflow like n8n.
# It receives a 3D model file (STL or OBJ), generates a preview image, and returns it.

import os
import io
import tempfile
import trimesh
from flask import Flask, request, send_file, jsonify

# --- IMPORTANT FOR DEPLOYMENT ---
# Add 'gunicorn' to your requirements.txt file for production deployment.
# Also, ensure you have a 'Procfile' in your repository with the line: web: gunicorn main:app

# Initialize the Flask application
app = Flask(__name__)

# Define the route for rendering the 3D model
@app.route('/render-stl', methods=['POST'])
def render_stl():
    """
    Handles the POST request to render a 3D model file.
    Expects a multipart/form-data request with a file part named 'file'.
    """
    # --- 1. Validate the incoming request ---
    # Check if the 'file' part is present in the request files
    if 'file' not in request.files:
        # If not, return a 400 Bad Request error with a helpful message
        return jsonify({"error": "No file part in request. Make sure the field is named 'file'."}), 400

    file = request.files['file']

    # Check if a filename is present, which indicates a file was actually selected/sent
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # --- 2. Save the uploaded file to a temporary location ---
    # Get the file extension (e.g., '.stl') to create the temp file correctly
    suffix = os.path.splitext(file.filename)[1]
    
    # Create a temporary file to store the uploaded model data
    # 'delete=False' is important so we can get its path before it's auto-deleted
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file.save(temp_file)
        temp_path = temp_file.name

    try:
        # --- 3. Load the model and generate the image using trimesh ---
        # Load the mesh from the temporary file path. 'force='mesh'' ensures it's treated as a mesh.
        mesh = trimesh.load(temp_path, force='mesh')

        # Create a scene from the mesh. This is necessary for rendering.
        scene = mesh.scene()

        # Save the scene as a PNG image in memory (as bytes)
        # You can adjust the resolution here if needed.
        png_bytes = scene.save_image(resolution=(600, 600), visible=True)

        # --- 4. Return the generated image ---
        # Send the image bytes back as a response.
        # 'io.BytesIO' creates an in-memory binary stream from the bytes.
        return send_file(
            io.BytesIO(png_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name='preview.png'
        )
    except Exception as e:
        # If any error occurs during processing, return a 500 Internal Server Error
        app.logger.error(f"Error processing file: {e}") # Log the error for debugging
        return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500
    finally:
        # --- 5. Clean up ---
        # This block always runs, ensuring the temporary file is deleted
        # whether the process succeeded or failed.
        if os.path.exists(temp_path):
            os.remove(temp_path)

# This block is now only for local development.
# The production server (Gunicorn) will run the 'app' object directly.
if __name__ == '__main__':
    # Get the port from the environment variable PORT, with a default for local testing
    port = int(os.environ.get('PORT', 5001))
    # Run the app, listening on all interfaces, which is required for containers
    app.run(debug=True, host='0.0.0.0', port=port)
