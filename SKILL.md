---
name: x-video-extractor
description: Extract key findings and insights from X/Twitter video posts. Use when the user shares an X or Twitter URL (x.com, twitter.com) containing a video and wants the key takeaways, ideas, arguments, or any knowledge from the video. Also use when the user wants to analyze, summarize, repurpose, or reference an X/Twitter video's content.
compatibility: "Requires Python 3.10+, ffmpeg, yt-dlp, and openai-whisper. macOS recommended (uses Homebrew for setup)."
---

# X Video Extractor

Extract key findings and insights from X/Twitter video posts. The script handles the mechanical work (download, transcribe, capture frames) — your job as the agent is to synthesize the key takeaways from the raw output.

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

## Workflow

The script saves the raw extraction to disk. You then read it, synthesize the key findings, and present those to the user. The raw transcript is an archive — never the final output.

### Step 1: Extract and save to a temp location

Always use `--save-dir` so the raw extraction lands on disk instead of stdout. This keeps the full transcript out of your context window.

```bash
python3 scripts/extract_video.py "POST_URL" --save-dir /tmp/x-extract
```

For long videos (10+ minutes), reduce frame noise:

```bash
python3 scripts/extract_video.py "POST_URL" --save-dir /tmp/x-extract --frame-interval 10.0
```

### Step 2: Read the extraction selectively

Don't read the entire file into context. Instead:

1. **Read the metadata section** (first ~20 lines) to understand who, when, and what the video is about
2. **Skim the transcript in chunks** — read the first few hundred lines, identify the structure, then read sections that seem substantive. Skip filler, repetition, and Q&A pleasantries.
3. **Check key frames** — use the Read tool on a handful of frames (especially early ones) to catch slides, diagrams, or text overlays that aren't captured in the audio

### Step 3: Synthesize key findings

From what you've read, produce a summary that captures:

- **Who** is speaking and their credibility/context
- **Core argument or thesis** — the main idea in 1-2 sentences
- **Key findings** — the 3-10 most important insights, frameworks, or pieces of advice
- **Notable quotes** — only if they're genuinely memorable or quotable
- **Actionable takeaways** — what should the viewer do differently after watching this?

Do not produce a chronological play-by-play. Group ideas by theme, not by timestamp.

### Step 4: Store or present

- If the user has a knowledge system (e.g., Obsidian vault), offer to store the findings in the appropriate format
- If not, present the synthesis directly
- The raw extraction stays on disk as an archive the user can reference later

## Tips for Long Videos

X/Twitter videos can be much longer than Instagram Reels (30+ minutes for talks and interviews). For long videos:

- Use `--frame-interval 5.0` or `--frame-interval 10.0` to reduce frame count
- Use `--whisper-model base` (default) for speed, upgrade to `small` only if quality is poor
- Use `--no-frames` if you only need the transcript
- **Read the transcript in chunks** rather than all at once — skim for structure first, then deep-read the substantive sections

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
