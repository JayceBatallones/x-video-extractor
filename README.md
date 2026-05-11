# X Video Extractor

A [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) that extracts transcripts, metadata, and key frames from X/Twitter video posts.

Built for use with Claude Code's skill system — drop the URL, get a structured markdown extraction with full transcript, engagement metrics, and visual frame captures.

## What It Does

Given an X/Twitter post URL containing a video, this tool extracts:

- **Transcript** with timestamps (via OpenAI Whisper)
- **Metadata** — creator, handle, upload date, duration
- **Engagement** — likes, reposts, comments
- **Caption** — original post text
- **Key frames** — screenshots at configurable intervals

Output is structured markdown with YAML frontmatter, ready to drop into Obsidian, Notion, or any markdown-based knowledge system.

## Requirements

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/)
- [openai-whisper](https://github.com/openai/whisper)

## Quick Start

### Option 1: As a Claude Code Skill

Symlink into your skills directory:

```sh
ln -sfn "$(pwd)" "$HOME/.claude/skills/x-video-extractor"
```

Then share an X video URL with Claude and it will use the skill automatically.

### Option 2: Standalone

```sh
# Install dependencies
bash setup.sh

# Extract a video
python3 scripts/extract_video.py "https://x.com/user/status/123456"

# Save to a directory
python3 scripts/extract_video.py "https://x.com/user/status/123456" --save-dir ~/notes/videos
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--save-dir DIR` | Save extraction to a directory | stdout only |
| `--whisper-model MODEL` | Whisper model size (tiny/base/small/medium/large) | `base` |
| `--json` | Output raw JSON instead of markdown | off |
| `--no-frames` | Skip frame extraction | off |
| `--no-transcript` | Skip transcription (metadata only) | off |
| `--frame-interval N` | Seconds between frame captures | `2.0` |
| `--cookies-from BROWSER` | Browser to extract cookies from | none |

## Examples

Basic extraction:
```sh
python3 scripts/extract_video.py "https://x.com/elonmusk/status/123"
```

Long talk with fewer frames:
```sh
python3 scripts/extract_video.py "https://x.com/speaker/status/456" \
  --frame-interval 10.0 --whisper-model small
```

Just metadata, no audio processing:
```sh
python3 scripts/extract_video.py "https://x.com/user/status/789" \
  --no-transcript --no-frames
```

## License

MIT
