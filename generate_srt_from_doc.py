import docx
import win32com.client
from datetime import timedelta

# ✅ Read .docx files
def read_docx_transcript(path):
    doc = docx.Document(path)
    return [para.text for para in doc.paragraphs if para.text.strip()]

# ✅ Read .doc files (Windows-only)
def read_doc_transcript(path):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()
    return text.split("\r\n")

# ✅ Format time for SRT
def format_srt_time(seconds):
    td = timedelta(seconds=seconds)
    return str(td)[:-3].zfill(8).replace('.', ',')

# ✅ Generate the SRT file
def generate_srt_from_transcript(transcript_lines, media_path, output_srt):
    print("🛠 Generating SRT content...")
    srt_content = ""
    start_time = 0
    duration_per_line = 3  # seconds

    for idx, line in enumerate(transcript_lines):
        if not line.strip():
            continue
        start = format_srt_time(start_time)
        end = format_srt_time(start_time + duration_per_line)
        srt_content += f"{idx+1}\n{start} --> {end}\n{line.strip()}\n\n"
        start_time += duration_per_line

    with open(output_srt, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    print(f"📝 SRT file written successfully to: {output_srt}")

