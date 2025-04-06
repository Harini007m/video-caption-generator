import os
from flask import Flask, render_template, request, redirect, url_for
import win32com.client
import pythoncom

# Function to read .doc files
def read_doc_transcript(path):
    pythoncom.CoInitialize()  # Initialize the COM library
    word = win32com.client.Dispatch("Word.Application")
    doc = word.Documents.Open(path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()
    return text.split("\r\n")  # Split text by new lines

# Your other imports
from generate_srt_from_doc import generate_srt_from_transcript, read_docx_transcript

app = Flask(__name__)

# Folders for uploading and saving files
UPLOAD_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

# Ensure these folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Home page route that serves the upload form
@app.route('/')
def index():
    status = request.args.get('status', '')
    return render_template('upload.html', status=status)


# Route to handle the file upload and subtitle generation
@app.route('/generate', methods=['POST'])
def generate():
    transcript = request.files['transcript']
    media = request.files['media']

    if transcript and media:
        # Save the uploaded files
        transcript_path = os.path.join(app.config['UPLOAD_FOLDER'], transcript.filename)
        media_path = os.path.join(app.config['UPLOAD_FOLDER'], media.filename)

        transcript.save(transcript_path)
        media.save(media_path)

        # Process the transcript based on its format
        if transcript.filename.endswith('.docx'):
            lines = read_docx_transcript(transcript_path)
        elif transcript.filename.endswith('.doc'):
            lines = read_doc_transcript(transcript_path)  # Call your function for .doc files
        else:
            return "❌ Invalid transcript format. Only .doc and .docx files are accepted.", 400

        # Generate SRT file from transcript and video/audio
        output_srt = os.path.join(app.config['OUTPUT_FOLDER'], os.path.splitext(media.filename)[0] + ".srt")
        generate_srt_from_transcript(lines, media_path, output_srt)

        # Redirect to the home page with a success message
        return redirect(url_for('index', status='success'))

    return "❌ Upload failed. Please ensure both files are uploaded correctly.", 400

if __name__ == '__main__':
    app.run(debug=True)
