#!/usr/bin/env python3
"""Extract transcript, metadata, and key frames from X/Twitter video posts."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


def check_dependencies():
    missing = []
    for cmd in ("yt-dlp", "ffmpeg"):
        if not shutil.which(cmd):
            missing.append(cmd)
    try:
        import whisper  # noqa: F401
    except ImportError:
        missing.append("openai-whisper (pip3 install openai-whisper)")
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def download_video(url, work_dir, cookies_from=None):
    cmd = [
        "yt-dlp",
        "-o", str(work_dir / "video.%(ext)s"),
        "--write-info-json",
        "-o", f"infojson:{work_dir / 'info.json'}",
        url,
    ]
    if cookies_from:
        cmd.extend(["--cookies-from", cookies_from])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"yt-dlp error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    video_files = list(work_dir.glob("video.*"))
    video_files = [f for f in video_files if f.suffix != ".json"]
    if not video_files:
        print("No video file downloaded", file=sys.stderr)
        sys.exit(1)

    info_path = work_dir / "info.json.info.json"
    if not info_path.exists():
        info_path = work_dir / "info.json"

    info = {}
    if info_path.exists():
        with open(info_path) as f:
            info = json.load(f)

    return video_files[0], info


def extract_audio(video_path, work_dir):
    audio_path = work_dir / "audio.wav"
    subprocess.run(
        [
            "ffmpeg", "-i", str(video_path),
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            str(audio_path),
            "-y", "-loglevel", "error",
        ],
        check=True,
    )
    return audio_path


def transcribe(audio_path, model_name="base"):
    import whisper

    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio_path))
    return result


def extract_frames(video_path, output_dir, interval=2.0):
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-i", str(video_path),
            "-vf", f"fps=1/{interval}",
            "-q:v", "2",
            str(output_dir / "frame_%04d.jpg"),
            "-y", "-loglevel", "error",
        ],
        check=True,
    )
    return sorted(output_dir.glob("frame_*.jpg"))


def format_timestamp(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_duration(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def build_markdown(url, info, transcription, frame_paths, frame_interval):
    lines = []

    creator = info.get("uploader", "Unknown")
    handle = info.get("uploader_id", "")
    title = info.get("title", "")
    description = info.get("description", "")
    duration = info.get("duration", 0)
    upload_date_raw = info.get("upload_date", "")
    like_count = info.get("like_count")
    repost_count = info.get("repost_count")
    comment_count = info.get("comment_count")

    upload_date = ""
    if upload_date_raw:
        try:
            upload_date = datetime.strptime(upload_date_raw, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            upload_date = upload_date_raw

    lines.append("---")
    lines.append("type: source")
    lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("medium: video")
    lines.append(f"url: {url}")
    lines.append("platform: x/twitter")
    lines.append(f"tags: []")
    lines.append("---")
    lines.append("")
    lines.append(f"# {creator} — X Video")
    lines.append("")
    lines.append(f"**URL:** {url}")
    lines.append(f"**Creator:** {creator} (@{handle})" if handle else f"**Creator:** {creator}")
    if upload_date:
        lines.append(f"**Date:** {upload_date}")
    if duration:
        lines.append(f"**Duration:** {format_duration(duration)}")

    metrics = []
    if like_count is not None:
        metrics.append(f"{like_count:,} likes")
    if repost_count is not None:
        metrics.append(f"{repost_count:,} reposts")
    if comment_count is not None:
        metrics.append(f"{comment_count:,} comments")
    if metrics:
        lines.append(f"**Engagement:** {', '.join(metrics)}")

    lines.append("")

    if description:
        lines.append("## Caption")
        lines.append("")
        lines.append(f"> {description}")
        lines.append("")

    if transcription and transcription.get("segments"):
        lang = transcription.get("language", "unknown")
        lines.append(f"## Transcript (language: {lang})")
        lines.append("")
        for seg in transcription["segments"]:
            ts = format_timestamp(seg["start"])
            text = seg["text"].strip()
            lines.append(f"**[{ts}]** {text}")
        lines.append("")

    if frame_paths:
        lines.append("## Key Frames")
        lines.append("")
        for i, fp in enumerate(frame_paths):
            ts = format_timestamp(i * frame_interval)
            lines.append(f"- `[{ts}]` ![]({fp.name})")
        lines.append("")

    return "\n".join(lines)


def build_json_output(url, info, transcription, frame_paths, frame_interval):
    return json.dumps(
        {
            "url": url,
            "creator": info.get("uploader"),
            "handle": info.get("uploader_id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "duration": info.get("duration"),
            "upload_date": info.get("upload_date"),
            "likes": info.get("like_count"),
            "reposts": info.get("repost_count"),
            "comments": info.get("comment_count"),
            "language": transcription.get("language") if transcription else None,
            "transcript": [
                {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
                for s in (transcription or {}).get("segments", [])
            ],
            "frames": [str(p) for p in (frame_paths or [])],
        },
        indent=2,
    )


def save_output(content, creator, upload_date, save_dir, frames_src=None):
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", (creator or "unknown").lower()).strip("-")
    date_str = upload_date or datetime.now().strftime("%Y-%m-%d")
    if len(date_str) == 8 and date_str.isdigit():
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    base_name = f"{slug}-x-video-{date_str}"
    out_file = save_path / f"{base_name}.md"
    counter = 2
    while out_file.exists():
        out_file = save_path / f"{base_name}-{counter}.md"
        counter += 1

    with open(out_file, "w") as f:
        f.write(content)

    if frames_src and frames_src.exists():
        frames_dest = save_path / f"{out_file.stem}-frames"
        if frames_src != frames_dest:
            shutil.copytree(frames_src, frames_dest, dirs_exist_ok=True)

    return out_file


def main():
    parser = argparse.ArgumentParser(description="Extract content from X/Twitter videos")
    parser.add_argument("url", help="X/Twitter post URL")
    parser.add_argument("--save-dir", help="Directory to save the extraction")
    parser.add_argument("--whisper-model", default="base", choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")
    parser.add_argument("--no-frames", action="store_true", help="Skip frame extraction")
    parser.add_argument("--no-transcript", action="store_true", help="Skip transcription (metadata only)")
    parser.add_argument("--frame-interval", type=float, default=2.0, help="Seconds between frame captures")
    parser.add_argument("--cookies-from", help="Browser to extract cookies from (chrome, firefox, etc.)")
    args = parser.parse_args()

    check_dependencies()

    with tempfile.TemporaryDirectory(prefix="x-extract-") as tmp:
        work_dir = Path(tmp)

        print("Downloading video...", file=sys.stderr)
        video_path, info = download_video(args.url, work_dir, args.cookies_from)

        transcription = None
        if not args.no_transcript:
            print("Extracting audio...", file=sys.stderr)
            audio_path = extract_audio(video_path, work_dir)

            print(f"Transcribing with whisper ({args.whisper_model})...", file=sys.stderr)
            transcription = transcribe(audio_path, args.whisper_model)

        frame_paths = []
        frames_dir = None
        if not args.no_frames:
            print("Extracting key frames...", file=sys.stderr)
            frames_dir = work_dir / "frames"
            frame_paths = extract_frames(video_path, frames_dir, args.frame_interval)
            print(f"Extracted {len(frame_paths)} frames", file=sys.stderr)

        if args.json:
            output = build_json_output(args.url, info, transcription, frame_paths, args.frame_interval)
        else:
            output = build_markdown(args.url, info, transcription, frame_paths, args.frame_interval)

        if args.save_dir:
            saved = save_output(
                output,
                info.get("uploader"),
                info.get("upload_date"),
                args.save_dir,
                frames_dir,
            )
            print(f"Saved to {saved}", file=sys.stderr)

        print(output)


if __name__ == "__main__":
    main()
