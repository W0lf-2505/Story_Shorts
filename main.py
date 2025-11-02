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
parser.add_argument("--gpu", action="store_true", help="Enable GPU accelerated rendering")
parser.add_argument("--sen", action="store_true", help="get sentence level captions")


args = parser.parse_args()
print(args)


from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

def group_words(captions, group_size=5):
    grouped = []
    for i in range(0, len(captions), group_size):
        chunk = captions[i:i + group_size]
        grouped.append(chunk)
    return grouped

HIGHLIGHT_COLORS = cycle([
    "#39FF14",  # Neon Green
    "#FF007F",  # Hot Pink
    "#00C6FF",  # Electric Blue
    "#FF8C00",  # Tangerine
    "#BF00FF",  # Vibrant Purple
])

def get_next_color():
    return next(HIGHLIGHT_COLORS)

def srt_to_moviepy_subtitles(srt_file, video_clip):
    subtitle_clips = []

    if args.sen:
            
        full_subs = group_words(pysrt.open(srt_file))
        for subs in full_subs:
            for sub in subs:

                start_time = sub.start.to_time()
                end_time = sub.end.to_time()
                start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond / 1e6
                end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second + end_time.microsecond / 1e6
                duration = end_seconds - start_seconds
                
                base_text = subs.text.replace('\n', ' ')  # full sentence
                word_text = sub.text.replace('\n', ' ')   # current word to highlight

                highlighted = f'<span font="Sans Bold 55" foreground="{get_next_color()}">{word_text}</span>'

                
                formatted_text = base_text.replace(word_text, highlighted, 1)
                formatted_text = f'<span font="Sans Bold 50" foreground="yellow">{formatted_text}</span>'

                # Create a text clip with a black background and white text
                text_clip = (TextClip(formatted_text, fontsize=50, color='yellow', method='pango', size=(video_clip.w - 20, None))
                    .set_start(start_seconds)
                    .set_duration(duration)
                    .set_position(('center', 'center')))  # Position center
                
                subtitle_clips.append(text_clip)


    else:    
        word_subs = pysrt.open(srt_file)

        for sub in word_subs:
            start_time = sub.start.to_time()
            end_time = sub.end.to_time()
            start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond / 1e6
            end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second + end_time.microsecond / 1e6
            duration = end_seconds - start_seconds
            
            formatted_text = '<span font="Sans Bold 70" foreground="'+get_next_color()+'">'+sub.text.replace('\n',' ') + '</span>'

            # Create a text clip with a black background and white text
            text_clip = (TextClip(formatted_text, fontsize=50, color='yellow', method='pango', size=(video_clip.w - 20, None))
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
        
    video_clip = resize(video_clip, height=1280)
    # Then crop width to 720 center
    w, h = video_clip.size
    x_center = w / 2
    video_clip = crop(video_clip, x1=x_center-360, x2=x_center+360)
    

    video_with_subs = srt_to_moviepy_subtitles(srt_file, video_clip)

    if args.gpu:
        print("Using GPU encoding (h264_nvenc)")
        video_with_subs.write_videofile(
            args.output,
            codec="h264_nvenc",
            fps=30,
            bitrate="3500k",
            ffmpeg_params=[
                "-preset", "p5",
                "-rc", "vbr",
                "-pix_fmt", "yuv420p",   # REQUIRED to prevent green frames
                "-profile:v", "high",
                "-movflags", "+faststart",
                "-c:a", "copy"           # Keep original audio exactly
            ]
        )

    else:
        print("Using CPU encoding (libx264)")
        video_with_subs.write_videofile(output_file,codec="libx264",
        fps=30,
        bitrate="3500k",
        ffmpeg_params=["-preset", "fast", "-movflags", "+faststart"]
    )

burn_subtitles(args.bg, args.srt, args.audio, args.output)

