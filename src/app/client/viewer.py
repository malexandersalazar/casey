import os
import cv2
import uuid
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory

class CaseySee:
    def __init__(self):
        self.app = Flask(__name__)
        self.__setup_routes()

    def __setup_routes(self):
        @self.app.route('/scripts/<path:filename>')
        def download_script(filename):
            return send_from_directory('wwwroot/scripts', filename)

        @self.app.route('/models/<path:filename>')
        def download_file(filename):
            return send_from_directory('wwwroot/models', filename)

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/save_emotion/<string:emotion>', methods=['POST'])
        def save_emotion(emotion):
            if 'image' not in request.files:
                return jsonify({'error': 'No image file'}), 400
            
            if not emotion:
                return jsonify({'error': 'No emotion specified'}), 400
            
            file = request.files['image']
            npimg = np.fromfile(file, np.uint8)
            img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

            # Create a directory for the emotion if it doesn't exist
            emotion_dir = os.path.join('client/data/captured_emotions', emotion)
            os.makedirs(emotion_dir, exist_ok=True)
            
            # Save the image in the corresponding emotion directory
            filename = f'{uuid.uuid4()}.jpg'
            filepath = os.path.join(emotion_dir, filename)
            cv2.imwrite(filepath, img)
            
            return jsonify({'message': 'Image saved successfully', 'emotion': emotion, 'filename': filename}), 200
        
    def run(self):
        self.app.run(debug=True)

if __name__ == "__main__":
    casey_see = CaseySee()
    casey_see.run()