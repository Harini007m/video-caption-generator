# model/transcriber.py
import whisper
import srt
import datetime

model = whisper.load_model("base")

def transcribe_video(video_path):
    result = model.transcribe(video_path)
    segments = result['segments']

    subtitles = []
    for i, seg in enumerate(segments):
        start = datetime.timedelta(seconds=int(seg['start']))
        end = datetime.timedelta(seconds=int(seg['end']))
        content = seg['text'].strip()

        # Format to max 2 lines, 65 chars per line
        words = content.split()
        lines, line = [], ''
        for word in words:
            if len(line + word) + 1 <= 65:
                line += word + ' '
            else:
                lines.append(line.strip())
                line = word + ' '
        lines.append(line.strip())
        lines = lines[:2]

        subtitle = srt.Subtitle(index=i+1, start=start, end=end, content='\n'.join(lines))
        subtitles.append(subtitle)

    return srt.compose(subtitles)
