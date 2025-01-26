from flask import Flask, render_template, request, send_from_directory
import os
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
RESIZED_FOLDER = 'static/resized'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESIZED_FOLDER'] = RESIZED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESIZED_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file is uploaded
        if 'image' not in request.files:
            return "No file uploaded!", 400
        
        file = request.files['image']
        if file.filename == '':
            return "No selected file!", 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Resize logic
        try:
            new_width = int(request.form.get('width'))
            new_height = int(request.form.get('height'))
        except (ValueError, TypeError):
            return "Invalid width or height!", 400
        
        src = cv2.imread(filepath)
        resized_image = cv2.resize(src, (new_width, new_height))
        
        # Save the resized image
        resized_filename = f"resized_{filename}"
        resized_filepath = os.path.join(app.config['RESIZED_FOLDER'], resized_filename)
        cv2.imwrite(resized_filepath, resized_image)
        
        # Pass the resized file's path to the frontend
        return render_template('index.html', resized_image=resized_filename)
    
    return render_template('index.html', resized_image=None)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['RESIZED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
