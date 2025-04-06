from flask import Flask, render_template, request, redirect, url_for
import os
from generate_srt_from_doc import generate_srt_from_transcript, read_docx_transcript, read_doc_transcript

app = Flask(__name__)
UPLOAD_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/generate', methods=['POST'])
def generate():
    transcript = request.files['transcript']
    media = request.files['media']

    if transcript and media:
        transcript_path = os.path.join(UPLOAD_FOLDER, transcript.filename)
        media_path = os.path.join(UPLOAD_FOLDER, media.filename)

        transcript.save(transcript_path)
        media.save(media_path)

        # Read transcript
        if transcript.filename.endswith('.docx'):
            lines = read_docx_transcript(transcript_path)
        elif transcript.filename.endswith('.doc'):
            lines = read_doc_transcript(transcript_path)
        else:
            return "❌ Invalid transcript format", 400

        output_srt = os.path.join(OUTPUT_FOLDER, os.path.splitext(media.filename)[0] + ".srt")
        generate_srt_from_transcript(lines, media_path, output_srt)

        return redirect(url_for('index', status='success'))

    return "❌ Upload failed", 400

if __name__ == '__main__':
    app.run(debug=True)
