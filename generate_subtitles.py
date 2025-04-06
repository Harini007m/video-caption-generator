import os
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin"
import whisper
import ffmpeg
import srt
import datetime



def extract_audio(video_path, audio_path):
    # Use ffmpeg to extract audio from the video
    ffmpeg.input(video_path).output(audio_path, ac=1, ar='16000').run(overwrite_output=True)

def transcribe_audio(audio_path):
    # Load Whisper model
    model = whisper.load_model("base")  # You can change to "small", "medium", or "large" if needed
    result = model.transcribe(audio_path)
    return result["segments"]

def generate_srt(segments, srt_path):
    subtitles = []
    for i, seg in enumerate(segments):
        start = datetime.timedelta(seconds=int(seg['start']))
        end = datetime.timedelta(seconds=int(seg['end']))
        text = seg['text'].strip()

        # Break into 2 lines if too long (max 65 chars per line)
        words = text.split()
        lines = []
        line = ""
        for word in words:
            if len(line + " " + word) <= 65:
                line += " " + word if line else word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        subtitle = srt.Subtitle(index=i+1, start=start, end=end, content="\n".join(lines[:2]))
        subtitles.append(subtitle)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))

def main():
    video_path = r"C:\Users\harin\Videos\Cash Holdings Feature in Manual Portfolios.mp4"    # Replace with your actual video file
    audio_path = "audio.wav"
    srt_path = "captions.srt"

    print("🔊 Extracting audio...")
    extract_audio(video_path, audio_path)

    print("🧠 Transcribing audio with Whisper...")
    segments = transcribe_audio(audio_path)

    print("📝 Generating .srt subtitle file...")
    generate_srt(segments, srt_path)

    print(f"✅ Done! Subtitles saved to {srt_path}")

if __name__ == "__main__":
    main()
