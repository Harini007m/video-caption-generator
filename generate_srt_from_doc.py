import os
import datetime
import srt
import re

from docx import Document
import win32com.client as win32


def read_docx_transcript(path):
    doc = Document(path)
    lines = []
    for para in doc.paragraphs:
        if para.text.strip():
            lines.append(para.text.strip())
    return lines


def read_doc_transcript(path):
    word = win32.gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(path)
    full_text = ""
    for para in doc.Paragraphs:
        full_text += para.Range.Text
    doc.Close(False)
    word.Quit()
    lines = [line.strip() for line in full_text.split("\r") if line.strip()]
    return lines


def get_media_duration(media_path):
    try:
        import ffmpeg
        probe = ffmpeg.probe(media_path)
        return float(probe['format']['duration'])
    except Exception as e:
        print("⚠️ FFmpeg not available or failed to read duration.")
        while True:
            try:
                duration = float(input("🕒 Enter total duration of media in seconds (e.g., 120.5): "))
                return duration
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.")


def generate_srt_from_transcript(lines, media_path, output_path):
    duration = get_media_duration(media_path)
    total_lines = len(lines)
    duration_per_line = duration / total_lines

    subtitles = []
    for i, line in enumerate(lines):
        start_sec = i * duration_per_line
        end_sec = (i + 1) * duration_per_line

        start = datetime.timedelta(seconds=int(start_sec))
        end = datetime.timedelta(seconds=int(end_sec))

        # Split line if too long
        words = line.split()
        lines_out = []
        temp_line = ""
        for word in words:
            if len(temp_line + " " + word) <= 65:
                temp_line += " " + word if temp_line else word
            else:
                lines_out.append(temp_line)
                temp_line = word
        if temp_line:
            lines_out.append(temp_line)

        subtitle = srt.Subtitle(index=i + 1, start=start, end=end, content="\n".join(lines_out[:2]))
        subtitles.append(subtitle)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))


def main():
    print("📄 Enter full path to your transcript file (.docx or .doc):")
    transcript_path = input().strip().strip('"')

    if not os.path.exists(transcript_path):
        print("❌ Transcript file not found.")
        return

    print("🎞️ Enter full path to your video/audio file (.mp4/.mp3/.mpv):")
    media_path = input().strip().strip('"')

    if not os.path.exists(media_path):
        print("❌ Media file not found.")
        return

    try:
        if transcript_path.lower().endswith(".docx"):
            lines = read_docx_transcript(transcript_path)
        elif transcript_path.lower().endswith(".doc"):
            lines = read_doc_transcript(transcript_path)
        else:
            print("❌ Unsupported file format. Use .docx or .doc only.")
            return
    except Exception as e:
        print(f"❌ Error reading transcript: {e}")
        return

    base_name = os.path.splitext(os.path.basename(media_path))[0]
    os.makedirs("output", exist_ok=True)
    output_srt = os.path.join("output", f"{base_name}.srt")

    print("📝 Generating SRT subtitle file...")
    generate_srt_from_transcript(lines, media_path, output_srt)

    print(f"✅ Done! Subtitles saved to: {output_srt}")


if __name__ == "__main__":
    main()
