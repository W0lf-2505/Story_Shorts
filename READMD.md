# Subtitle Video Maker (Pango Karaoke Style)

This tool generates attention-grabbing karaoke-style subtitles on videos for Shorts.

## Usage

Place your files in the `input/` folder:
- background.mp4
- captions.srt
- audio.mp3

Then run:

```bash
docker run --rm \
  -v "$PWD/input:/input" \
  -v "$PWD/output:/output" \
  caption-maker \
  /input/captions.srt \
  /input/audio.mp3 \
  /input/background.mp4 \
  /output/final.mp4
