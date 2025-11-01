from moviepy.editor import TextClip, CompositeVideoClip , VideoFileClip , AudioFileClip
import pysrt
from moviepy.video.fx.all import resize, crop
from itertools import cycle
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("--srt", required=True, help="Path to subtitle .srt file")
parser.add_argument("--audio", required=True, help="Path to audio file")
parser.add_argument("--bg", required=True, help="Path to background video")
parser.add_argument("--output", required=True, help="Output rendered video path")

args = parser.parse_args()


def group_words(captions, group_size=5):
    grouped = []
    for i in range(0, len(captions), group_size):
        chunk = captions[i:i + group_size]
        grouped.append(chunk)
    return grouped

HIGHLIGHT_COLORS = cycle([
    "#FFEA00",  # Neon Yellow
    "#39FF14",  # Neon Green
    "#FF007F",  # Hot Pink
    "#00C6FF",  # Electric Blue
    "#FF8C00",  # Tangerine
    "#BF00FF",  # Vibrant Purple
])

def get_next_color():
    return next(HIGHLIGHT_COLORS)

def srt_to_moviepy_subtitles(srt_file, video_clip):
    full_subs = group_words(pysrt.open(srt_file))
    subtitle_clips = []

    # --- 2. Configuration ---
    VIDEO_FILE = "input.mp4"
    OUTPUT_FILE = "output_highlighted.mp4"
    FONT = "Arial"
    FONTSIZE = 40
    COLOR = 'white'
    HIGHLIGHT_COLOR = 'yellow'
    STROKE_COLOR = 'black'
    STROKE_WIDTH = 1.5
    POSITION = ("center", "center")

    for subs in full_subs:

        for sub in subs:

            
            start_time = sub.start.to_time()
            end_time = sub.end.to_time()
            start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond / 1e6
            end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second + end_time.microsecond / 1e6
            duration = end_seconds - start_seconds
            
            formatted_text = '<span font="Sans Bold 120" foreground="'+get_next_color()+'">'+sub.text.replace('\n',' ') + '</span>'

            # Create a text clip with a black background and white text
            text_clip = (TextClip(formatted_text, fontsize=70, color='yellow', method='pango', size=(video_clip.w - 20, None))
                .set_start(start_seconds)
                .set_duration(duration)
                .set_position(('center', 'center')))  # Position center
            
            subtitle_clips.append(text_clip)

    return CompositeVideoClip([video_clip] + subtitle_clips)


def burn_subtitles(video_file, srt_file, audio_file, output_file):
    video_clip = VideoFileClip(video_file).without_audio()
    audio = AudioFileClip(audio_file)
    video_clip = video_clip.set_audio(audio)
        
    video_clip = video_clip.subclip(0, audio.duration)
        
    video_clip = resize(video_clip, height=1920)
    # Then crop width to 1080 center
    w, h = video_clip.size
    x_center = w / 2
    video_clip = crop(video_clip, x1=x_center-540, x2=x_center+540)
    

    video_with_subs = srt_to_moviepy_subtitles(srt_file, video_clip)
    video_with_subs.write_videofile(output_file, codec='libx264')

burn_subtitles(args.bg, args.srt, args.audio, args.output)

