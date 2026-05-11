---
name: x-video-extractor
description: Extract transcript, metadata, and key frames from X/Twitter video posts. Use when the user shares an X or Twitter URL (x.com, twitter.com) containing a video and wants the transcript, speaker info, engagement metrics, or any data from the video. Also use when the user wants to analyze, repurpose, or reference an X/Twitter video's content.
compatibility: "Requires Python 3.10+, ffmpeg, yt-dlp, and openai-whisper. macOS recommended (uses Homebrew for setup)."
---

# X Video Extractor

Extract the spoken transcript, metadata, and key frames from X/Twitter video posts.

## Prerequisites

The following must be installed on the user's machine:

- **yt-dlp** — `brew install yt-dlp`
- **ffmpeg** — `brew install ffmpeg`
- **Python packages** — `pip3 install openai-whisper`

Or run the setup script: `bash setup.sh`

If any dependency is missing, tell the user which ones to install before proceeding.

## Usage

Run the extraction script with the post URL:

```bash
python3 scripts/extract_video.py "POST_URL"
```

Save the extraction to a specific directory:

```bash
python3 scripts/extract_video.py "POST_URL" --save-dir ~/notes/videos
```

For better transcription accuracy (slower, uses more memory):

```bash
python3 scripts/extract_video.py "POST_URL" --whisper-model small
```

For raw JSON output:

```bash
python3 scripts/extract_video.py "POST_URL" --json
```

Skip frame extraction (faster, audio/metadata only):

```bash
python3 scripts/extract_video.py "POST_URL" --no-frames
```

Skip transcription (metadata and frames only):

```bash
python3 scripts/extract_video.py "POST_URL" --no-transcript
```

Adjust frame interval (default every 2 seconds):

```bash
python3 scripts/extract_video.py "POST_URL" --frame-interval 5.0
```

## What Gets Extracted

- **Original URL** — link back to the source post (always included)
- **Creator** — display name and handle
- **Metrics** — likes, reposts, comments count (as of extraction date)
- **Caption** — the original post text
- **Duration** — video length
- **Upload date**
- **Transcript** — full spoken text from the audio, with timestamps
- **Language** — auto-detected language of the speech
- **Key frames** — screenshots extracted every N seconds, saved as JPGs with timestamps

## Output

The script outputs a structured markdown summary with YAML frontmatter and the original URL at the top. Present this to the user as-is — do not modify the transcript text itself, though you can clean up line breaks and paragraph flow for readability.

When frames are extracted, they are saved to a `frames/` subdirectory. When presenting the extraction, use the Read tool to view the frame images so you can describe what's happening visually at each timestamp (slides, speaker, diagrams, text overlays, etc.).

When `--save-dir` is provided, the extraction is automatically saved as `<creator>-x-video-<upload_date>.md`. Frames are saved to a matching `-frames/` subdirectory. If a file already exists, a number is appended.

## Configuring a Default Save Location

To always save extractions to a specific folder, tell Claude: "save X video extractions to ~/my/folder". Claude will pass `--save-dir` automatically on future runs.

## Tips for Long Videos

X/Twitter videos can be much longer than Instagram Reels (30+ minutes for talks and interviews). For long videos:

- Use `--frame-interval 5.0` or `--frame-interval 10.0` to reduce frame count
- Use `--whisper-model base` (default) for speed, upgrade to `small` only if quality is poor
- Use `--no-frames` if you only need the transcript

## Whisper Model Sizes

| Model  | Speed    | Accuracy | Memory  |
|--------|----------|----------|---------|
| tiny   | Fastest  | Lower    | ~1 GB   |
| base   | Fast     | Good     | ~1 GB   |
| small  | Moderate | Better   | ~2 GB   |
| medium | Slow     | Great    | ~5 GB   |
| large  | Slowest  | Best     | ~10 GB  |

Default is `base` — a good balance for most content. Suggest `small` if the user reports transcription quality issues.

## Troubleshooting

- **Login required errors**: Some posts may require authentication. Pass `--cookies-from chrome` (or `firefox`) to use browser cookies.
- **No speech detected**: The video may be music-only or use on-screen text instead of speech. Let the user know and suggest `--no-transcript` with frames to capture the visual content.
- **Slow transcription**: Whisper runs on CPU by default. On Apple Silicon Macs, it uses the Neural Engine automatically. For faster runs on long videos, suggest the `tiny` model.
- **Rate limiting**: If yt-dlp fails with rate-limit errors, wait a minute and retry, or use `--cookies-from` to authenticate.
