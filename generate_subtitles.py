import os
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin"
import whisper
import ffmpeg
import srt
import datetime


def extract_audio(video_path, audio_path):
    # Use ffmpeg to extract audio from video
    ffmpeg.input(video_path).output(audio_path, ac=1, ar='16000').run(overwrite_output=True)


def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["segments"]


def generate_srt(segments, srt_path):
    subtitles = []
    for i, seg in enumerate(segments):
        start = datetime.timedelta(seconds=int(seg['start']))
        end = datetime.timedelta(seconds=int(seg['end']))
        text = seg['text'].strip()

        # Break text into two lines if too long (max 65 chars per line)
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
    print("📁 Please enter the full path to your video/audio file (.mp4/.mp3/.mpv):")
    file_path = input().strip()

    if not os.path.exists(file_path):
        print("❌ File not found. Please check the path and try again.")
        return

    # Determine if audio extraction is needed
    extension = os.path.splitext(file_path)[1].lower()
    audio_path = "audio.wav"

    # Auto name for .srt file
    srt_path = os.path.splitext(os.path.basename(file_path))[0] + ".srt"

    if extension in [".mp4", ".mpv"]:
        print("🔊 Extracting audio from video...")
        extract_audio(file_path, audio_path)
    elif extension == ".mp3":
        print("🔄 Converting .mp3 to .wav...")
        ffmpeg.input(file_path).output(audio_path, ac=1, ar='16000').run(overwrite_output=True)
    else:
        print("❌ Unsupported file format. Please use .mp4, .mp3, or .mpv.")
        return

    print("🧠 Transcribing audio with Whisper...")
    segments = transcribe_audio(audio_path)

    print("📝 Generating .srt subtitle file...")
    generate_srt(segments, srt_path)

    print(f"✅ Done! Subtitles saved to {srt_path}")


if __name__ == "__main__":
    main()
