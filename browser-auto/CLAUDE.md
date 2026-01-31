# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

ragebAIt is a CLI tool that posts an image, a video, and a caption together to X (Twitter) using browser-use with local Chrome automation. Media and descriptions are provided by the user — there is no AI caption generation.

## Commands

```bash
uv sync                                    # install dependencies
uv run main.py <image> <video> "<caption>"  # post with CLI args
uv run main.py                             # interactive mode (picks image + video)
```

## Architecture

Two-file design:

- **main.py** — Entry point. Accepts an image file, a video file, and a caption (via CLI args or interactive prompts). Validates both files, runs a Y/E/S confirmation loop, then calls `poster.post_to_x()`.
- **poster.py** — Launches local Chrome using the user's existing profile (Default) via browser-use. A `ChatGoogle` agent (gemini-3-flash-preview) navigates x.com, composes a post with the caption, attaches both the image and video (via `available_file_paths`), and publishes.

The flow is linear: input (image + video + caption) → confirm → browser agent posts with both files → report result.

## Key Details

- Uses `uv` for dependency management (pyproject.toml, not requirements.txt).
- Local Chrome automation — no cloud browser needed. Chrome must be fully closed before running.
- Authentication is via the user's existing Chrome profile with saved cookies. The env var `GEMINI_API_KEY` is required for the LLM.
- Both media files are referenced by absolute local path and must be whitelisted via `available_file_paths` on the Agent for browser-use to allow uploads.
- Supported image formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`. Supported video formats: `.mp4`, `.mov`. Each post requires one image and one video.
- Python 3.14+.
