from flask import Flask
from flask_cors import CORS, cross_origin

import apis
from containers import Container

def create_app(container: Container):
    app = Flask(__name__)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'   
    app.container = container
    app.add_url_rule("/api/hello", None, lambda: 'Hello World!', methods=["GET"])

    upload_audio = cross_origin(expose_headers=['X-Emotion'])(apis.upload_audio)
    app.add_url_rule("/api/upload-audio", None, upload_audio, methods=["POST"])

    return app