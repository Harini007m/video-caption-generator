# app/routes.py
import os
from flask import Blueprint, request, render_template, send_file
from model.transcriber import transcribe_video

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['video']
        if file.filename.endswith('.mp4'):
            upload_path = os.path.join('uploads', file.filename)
            caption_path = os.path.join('captions', file.filename.replace('.mp4', '.srt'))

            file.save(upload_path)
            srt_result = transcribe_video(upload_path)

            with open(caption_path, 'w', encoding='utf-8') as f:
                f.write(srt_result)

            return send_file(caption_path, as_attachment=True)

    return render_template('index.html')
