# X Video Extractor

Extract key findings, insights, and takeaways from X/Twitter video posts. The tool downloads the video, transcribes the audio, and captures key frames — giving you or your AI agent everything needed to distill the content without watching it.

Works as a standalone CLI tool, a Claude Code skill, or with any AI coding agent that can run shell commands.

## Prerequisites

The following must be installed on the user's machine:

- **yt-dlp** — `brew install yt-dlp`
- **ffmpeg** — `brew install ffmpeg`
- **Python packages** — `pip3 install openai-whisper`

Or run the setup script: `bash setup.sh`

If any dependency is missing, install them before proceeding.

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

The script captures the raw material an AI agent (or human) needs to identify the key findings:

- **Transcript** — full spoken text with timestamps, so nothing gets missed
- **Key frames** — screenshots at regular intervals capturing slides, diagrams, and text overlays that aren't in the audio
- **Metadata** — creator, handle, upload date, duration, engagement metrics, and the original caption

The goal is not to replicate the video — it's to make the knowledge inside it searchable, synthesizable, and reusable.

## Output

The script outputs a structured markdown summary with YAML frontmatter and the original URL at the top. Feed this to an AI agent to summarize key findings, or read the transcript yourself.

When frames are extracted, they are saved to a `frames/` subdirectory alongside the markdown file.

When `--save-dir` is provided, the extraction is automatically saved as `<creator>-x-video-<upload_date>.md`. Frames are saved to a matching `-frames/` subdirectory. If a file already exists, a number is appended.

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
- **No speech detected**: The video may be music-only or use on-screen text instead of speech. Use `--no-transcript` with frames to capture the visual content instead.
- **Slow transcription**: Whisper runs on CPU by default. On Apple Silicon Macs, it uses the Neural Engine automatically. For faster runs on long videos, suggest the `tiny` model.
- **Rate limiting**: If yt-dlp fails with rate-limit errors, wait a minute and retry, or use `--cookies-from` to authenticate.

## Using with AI Agents

### Claude Code

Symlink into your skills directory:

```sh
ln -sfn "$(pwd)" "$HOME/.claude/skills/x-video-extractor"
```

Then share an X video URL with Claude and it will use the skill automatically.

### Other Agents

Any AI coding agent that can execute shell commands can use this tool. Point it at `scripts/extract_video.py` and it will get structured markdown or JSON output. The `--json` flag is especially useful for agents that prefer to parse structured data.

## License

MIT
