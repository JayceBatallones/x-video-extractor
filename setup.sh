#!/usr/bin/env bash
set -euo pipefail

echo "=== X Video Extractor — Setup ==="

if ! command -v brew &>/dev/null; then
  echo "Homebrew not found. Install it from https://brew.sh"
  exit 1
fi

for tool in yt-dlp ffmpeg; do
  if command -v "$tool" &>/dev/null; then
    echo "✓ $tool already installed"
  else
    echo "Installing $tool..."
    brew install "$tool"
  fi
done

echo "Installing Python packages..."
pip3 install openai-whisper

echo ""
echo "=== Setup complete ==="
echo "Usage: python3 scripts/extract_video.py \"https://x.com/user/status/123\""
