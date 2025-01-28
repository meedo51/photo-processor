from flask import Flask, request, jsonify, render_template
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['MAX_FILE_SIZE'] = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_image(image_path, output_path, photo_type):
    try:
        # Open image and remove background
        input_image = Image.open(image_path)
        output_image = remove(input_image)

        # Resize based on photo type
        size = (600, 600) if photo_type == 'id' else (450, 600)
        output_image = ImageOps.fit(output_image, size, Image.ANTIALIAS)

        # Enhance image (brightness, contrast, sharpness)
        enhancer = ImageEnhance.Brightness(output_image)
        output_image = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Contrast(output_image)
        output_image = enhancer.enhance(1.1)

        # Save the processed image
        output_image.save(output_path)
        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a JPEG or PNG image.'})
    if file.content_length > app.config['MAX_FILE_SIZE']:
        return jsonify({'error': 'File size exceeds 5MB. Please upload a smaller file.'})

    try:
        # Save the uploaded file
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        # Process the image
        output_filename = 'output_' + filename
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        photo_type = request.form['type']
        if not process_image(image_path, output_path, photo_type):
            return jsonify({'error': 'Failed to process the image. Please try again.'})

        return jsonify({'image_url': output_path})
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing the image.'})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
