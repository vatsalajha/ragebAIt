# Social Media Poster Agent — MVP Design

## Overview
CLI tool that takes images/videos with their descriptions and uses Browser-Use Cloud to post them to X (Twitter) via browser automation.

## Architecture
```
 Input (media + caption)       Browser-Use Cloud          X (Twitter)
 ┌────────────────────┐       ┌───────────────────┐      ┌──────────┐
 │ image/video path   │──────▶│ Open X, upload     │─────▶│ Published│
 │ + description      │       │ media & post       │      │ Post     │
 └────────────────────┘       └───────────────────┘      └──────────┘
```

## Project Structure
```
ragebAIt/
├── main.py              # Entry point — reads input and triggers posting
├── poster.py            # Browser-Use Cloud: post media + caption to X
├── pyproject.toml       # Project config & dependencies (managed by uv)
├── .env.example         # Template for API keys
└── DESIGN.md            # This file
```

## Flow
```
1. User provides media file path + description (via CLI args or prompt)
2. Confirm post with user: [Y]es / [E]dit / [S]kip
3. If approved → Browser-Use Cloud agent posts to X with the file + caption
4. Report success/failure
```

## File Details

### `main.py` (~40 lines)
Entry point. Accepts a media file path and description, then hands off to the poster.

- Accepts CLI args: `python main.py <filepath> "<caption>"`
- Or prompts interactively if no args given
- Supported formats: `.jpg`, `.png`, `.gif`, `.webp`, `.mp4`, `.mov`
- Shows the caption, prompts user: `[Y]es / [E]dit / [S]kip`
- Calls `poster.post_to_x(filepath, caption)`
- Uses `asyncio.run()` as entry point

### `poster.py` (~30 lines)
Handles browser automation via Browser-Use Cloud to post on X.

- `async post_to_x(filepath: str, caption: str) -> bool`
- Uses a Browser-Use Cloud profile (already logged into X, no credentials needed):
  ```python
  from browser_use import Agent, Browser, ChatBrowserUse

  browser = Browser(
      cloud_profile_id=os.getenv("BROWSER_USE_PROFILE_ID"),
  )

  agent = Agent(
      task=f"Go to x.com. You are already logged in. "
           f"Create a new post with this text: '{caption}'. "
           f"Upload the file at '{abs_path}' as media attachment. "
           f"Then click the Post button to publish it.",
      llm=ChatBrowserUse(),
      browser=browser,
      max_steps=25,
  )

  result = await agent.run()
  ```
- Returns `True`/`False` based on success

## Dependencies

Managed via `uv` and `pyproject.toml`:
- `browser-use`
- `python-dotenv`

### `.env.example`
```
BROWSER_USE_API_KEY=your-browser-use-api-key
BROWSER_USE_PROFILE_ID=your-cloud-profile-id
```

## Browser-Use Cloud Setup

1. **Get an API key** — Sign up at [cloud.browser-use.com](https://cloud.browser-use.com) and grab your API key.
2. **Create a cloud profile** — In the Browser-Use Cloud dashboard, create a profile and log into X manually within that session. The cookies persist across runs.
3. **Set env vars** — Add `BROWSER_USE_API_KEY` and `BROWSER_USE_PROFILE_ID` to your `.env` file.

`cloud_profile_id` syncs cookies/auth from the profile, so the agent starts already logged in — no credentials are passed to the LLM. `ChatBrowserUse()` is the optimized model hosted by Browser-Use for driving the browser agent.

## How to Run
```bash
# 1. Install deps
uv sync

# 2. Copy and fill in keys
cp .env.example .env
# Edit .env with your BROWSER_USE_API_KEY and BROWSER_USE_PROFILE_ID

# 3. Run with a file and caption
uv run main.py ./photo.jpg "just vibes"

# Or run interactively
uv run main.py
```

## Verification
1. Run `uv run main.py ./test.jpg "test post please ignore"`
2. Approve the caption (type `y`)
3. Watch the cloud browser agent log in, navigate, and post
4. Check X to confirm the post appeared with correct caption + media
