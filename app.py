import os
from flask import Flask, render_template, request, redirect, url_for
import pythoncom
import win32com.client

# Your custom functions
from generate_srt_from_doc import generate_srt_from_transcript, read_docx_transcript

app = Flask(__name__)

# Updated folders: Save output in static/output for download
UPLOAD_FOLDER = 'input'
OUTPUT_FOLDER = os.path.join('static', 'output')

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# === Read .doc using COM ===
def read_doc_transcript(doc_path):
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"❌ Transcript file not found at: {doc_path}")

    pythoncom.CoInitialize()

    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        print(f"📂 Opening DOC file: {doc_path}")
        doc = word.Documents.Open(os.path.abspath(doc_path))
        text = doc.Content.Text
        doc.Close()
        return text.splitlines()
    except Exception as e:
        raise RuntimeError(f"❌ Failed to read .doc file: {str(e)}")
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

# === Routes ===

@app.route('/')
def index():
    status = request.args.get('status', '')
    filename = request.args.get('filename', '')
    return render_template('upload.html', status=status, filename=filename)

@app.route('/generate', methods=['POST'])
def generate():
    transcript = request.files.get('transcript')
    media = request.files.get('media')

    if not transcript or not media:
        return "❌ Upload failed. Please ensure both files are uploaded correctly.", 400

    # Save uploaded files
    transcript_filename = transcript.filename
    media_filename = media.filename

    transcript_path = os.path.join(app.config['UPLOAD_FOLDER'], transcript_filename)
    media_path = os.path.join(app.config['UPLOAD_FOLDER'], media_filename)

    transcript.save(transcript_path)
    media.save(media_path)

    print(f"✅ Saved transcript at: {transcript_path}")
    print(f"✅ Saved media at: {media_path}")

    try:
        # Read transcript
        if transcript_filename.endswith('.docx'):
            lines = read_docx_transcript(transcript_path)
        elif transcript_filename.endswith('.doc'):
            lines = read_doc_transcript(transcript_path)
        else:
            return "❌ Invalid transcript format. Only .doc and .docx files are accepted.", 400

        # Generate SRT with same name as media
        output_filename = os.path.splitext(media_filename)[0] + ".srt"
        output_srt_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        generate_srt_from_transcript(lines, media_path, output_srt_path)
        print(f"✅ SRT generated at: {output_srt_path}")

        # Redirect to show success with filename
        return redirect(url_for('index', status='success', filename=output_filename))

    except Exception as e:
        print(f"❌ Error: {e}")
        return f"❌ Error during processing: {e}", 500

# === Main ===
if __name__ == '__main__':
    app.run(debug=True)
