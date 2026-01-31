# YouTube Integration Plan

## Goal

Extend ragebAIt to upload videos to YouTube via Browser-Use Cloud, reusing the same browser automation pattern as the existing X (Twitter) poster. The user provides a video file and an image — the video gets uploaded and the image is set as the custom thumbnail.

## YouTube Upload Requirements

To publish a YouTube video, the browser agent needs to:

1. Navigate to [studio.youtube.com](https://studio.youtube.com)
2. Click "Create" → "Upload videos"
3. Select the video file
4. Set the title (from the caption)
5. Set the description (optional, can reuse caption or take separate input)
6. Upload a custom thumbnail (the image file)
7. Set visibility to Public
8. Click through the steps and publish

## New Env Vars

```
BROWSER_USE_YOUTUBE_PROFILE_ID=your-youtube-cloud-profile-id
```

A separate cloud profile pre-authenticated with a Google/YouTube account. Kept separate from the X profile since they're different auth sessions.

## File Changes

### 1. `poster.py` — Add `post_to_youtube()`

New function alongside `post_to_x()`:

```python
async def post_to_youtube(video_path: str, thumbnail_path: str, title: str, description: str) -> bool:
```

- Uses `BROWSER_USE_YOUTUBE_PROFILE_ID` for the cloud profile
- Browser agent task instructs navigation to studio.youtube.com, uploads the video, sets the title/description, uploads the custom thumbnail, sets visibility to Public, and publishes
- Same error handling pattern as `post_to_x()`
- `max_steps` should be higher (~40) since the YouTube upload flow has more screens (details, visibility, checks, publish)

Agent task string (rough):

```
Go to studio.youtube.com. You are already logged in.
Click the "Create" button, then "Upload videos".
Upload the video file at '{video_path}'.
Set the title to '{title}'.
Set the description to '{description}'.
Click on the thumbnail section and upload the custom thumbnail from '{thumbnail_path}'.
Under Visibility, select "Public".
Click through any remaining steps and publish the video.
```

### 2. `main.py` — Add platform selection and YouTube input flow

Changes to the entry point:

- **Platform prompt**: After getting the media file, ask the user which platform to post to: `[X] Twitter / [Y] YouTube`
- **YouTube input**: When YouTube is selected, require:
  - A video file (`.mp4`, `.mov`)
  - A thumbnail image (`.jpg`, `.png`, `.webp`)
  - A title (maps to YouTube video title)
  - A description (optional, defaults to the title)
- **CLI args**: Extend to support `--platform youtube --video <path> --thumbnail <path> --title "..." --description "..."`
- **Validation**: For YouTube, enforce that the video is `.mp4`/`.mov` and the thumbnail is an image format. YouTube also requires the channel to have phone verification for custom thumbnails — note this in docs.
- **Confirmation loop**: Same Y/E/S pattern, showing all fields

### 3. `.env.example` — Add YouTube profile ID

```
BROWSER_USE_API_KEY=your-browser-use-api-key
BROWSER_USE_PROFILE_ID=your-x-cloud-profile-id
BROWSER_USE_YOUTUBE_PROFILE_ID=your-youtube-cloud-profile-id
```

### 4. `CLAUDE.md` / `DESIGN.md` — Update docs

- Add YouTube to supported platforms
- Document the new CLI args and env vars
- Update the architecture diagram

## Updated CLI Interface

```bash
# Post to X (default, backwards compatible)
uv run main.py photo.jpg "just vibes"

# Post to YouTube
uv run main.py --platform youtube --video clip.mp4 --thumbnail thumb.jpg --title "My Video" --description "Check this out"

# Interactive mode (prompts for platform choice)
uv run main.py
```

## Updated Architecture

```
                          ┌─── poster.post_to_x()     ──▶  X (Twitter)
Input ─▶ Confirm ─▶ Route │
                          └─── poster.post_to_youtube() ──▶  YouTube
```

The routing is a simple if/else on the platform choice. No need for a plugin system or abstract base class at this stage — two explicit functions in `poster.py` is sufficient.

## Browser-Use Cloud Setup for YouTube

1. Create a new cloud profile in the Browser-Use Cloud dashboard
2. Open a browser session with that profile
3. Log into a Google account that owns a YouTube channel
4. Verify the channel has custom thumbnail permissions (phone verification)
5. Save the profile — cookies persist for future runs
6. Set `BROWSER_USE_YOUTUBE_PROFILE_ID` in `.env`

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| YouTube Studio UI is complex with multiple steps/screens | Increase `max_steps` to ~40; write a precise agent task string that walks through each screen |
| Custom thumbnail upload requires channel phone verification | Document this as a prerequisite in setup instructions |
| YouTube may show pop-ups or prompts (age restriction, audience, etc.) | Include instructions in the agent task to select defaults and dismiss dialogs |
| Video upload time depends on file size | Set a longer timeout; the browser agent should wait for the upload progress bar to complete before proceeding |
| YouTube may rate-limit or flag automated uploads | Use reasonable posting frequency; the cloud profile's cookies make it look like a normal session |

## Implementation Order

1. Add `post_to_youtube()` to `poster.py`
2. Update `main.py` with platform selection and YouTube input flow
3. Update `.env.example` with the new env var
4. Test with a real upload to YouTube Studio
5. Update `CLAUDE.md` and `DESIGN.md`
