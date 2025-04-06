import docx
import win32com.client  # This works only on Windows, you can try alternative methods for cross-platform

# Function for reading .docx files
def read_docx_transcript(path):
    doc = docx.Document(path)
    return [para.text for para in doc.paragraphs if para.text.strip()]

# Function for reading .doc files (Windows-only method)
def read_doc_transcript(path):
    word = win32com.client.Dispatch("Word.Application")
    doc = word.Documents.Open(path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()
    return text.split("\r\n")

# Function for generating SRT (stays the same)
def generate_srt_from_transcript(transcript_lines, media_path, output_srt):
    # Logic to create the SRT file from the transcript and video/audio
    pass
