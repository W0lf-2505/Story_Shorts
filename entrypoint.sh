#!/bin/bash
set -e

# Inputs from arguments
INPUT_SRT="$1"
INPUT_AUDIO="$2"
INPUT_BG="$3"
OUTPUT_VIDEO="$4"

python3 main.py \
  --srt "$INPUT_SRT" \
  --audio "$INPUT_AUDIO" \
  --bg "$INPUT_BG" \
  --output "$OUTPUT_VIDEO"
