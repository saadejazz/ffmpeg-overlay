import os
import ffmpeg
from PIL import Image
from os.path import join
from PIL.Image import Resampling

direct = "videos"
output = "output"

# make output directory if not already created
os.makedirs("output", exist_ok = True)

# retrieve all files from the input video folder
files = []
for (_, _, filenames) in os.walk(direct):
    files.extend(filenames)
files = [f for f in files if f.endswith(".mp4")]

for (idx, fi) in enumerate(files):

    # designate input and output file names
    file_name = join(direct, fi)
    fout = join(output, fi)

    # checking video dimensions
    probe = ffmpeg.probe(file_name)
    video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
    base_width = video_streams[0]['width'] - 20

    # resizing overlay to fit
    im = Image.open('overlay.png')
    width, height = im.size
    ratio = base_width/width
    im = im.resize((base_width, int(ratio * height)), Resampling.LANCZOS)
    im.save("temp.png")

    # get video and audio streams
    vid_stream = ffmpeg.input(file_name).video
    audio_stream = ffmpeg.input(file_name).audio
    vid_background = ffmpeg.input('temp.png')

    # overlay background on video stream and mix in original audio stream
    overlaid_vid_stream = ffmpeg.overlay(vid_stream, vid_background, x = 10, y = 10)
    output_video_and_audio = ffmpeg.output(audio_stream, overlaid_vid_stream, fout)
    output_video_and_audio.overwrite_output().run(quiet = False) # set quiet = True to remove output clutter

    # clean up
    os.remove("temp.png")

    # keep track of videos processed
    print("Processed", idx + 1, "videos")