# test_transcriber.py
from model.transcriber import transcribe_video

srt_output = transcribe_video("test_videos/sample.mp4")
with open("outputs/sample.srt", "w", encoding="utf-8") as f:
    f.write(srt_output)
