# Plan: Migrate from Browser-Use Cloud to Local Chrome

## Overview
Replace Browser-Use Cloud with local Chrome automation using the user's existing Chrome profile (Default). This eliminates the cloud presigned-URL upload mechanism entirely since local Chrome can access local files directly. Switches LLM from `ChatBrowserUse` (cloud-only) to `ChatGoogle` with `gemini-2.0-flash` (GEMINI_API_KEY already in .env).

## Files to Modify

### 1. `poster.py` — Rewrite (core change)

**Remove:**
- `import httpx`
- `MIME_TYPES` dictionary
- Entire `_upload_to_cloud_session()` function
- All references to `cloud_profile_id`, `session_id`, `cloud_filename`, `BROWSER_USE_API_KEY`, `BROWSER_USE_PROFILE_ID`

**Change:**
- `from browser_use import Agent, Browser, ChatBrowserUse` → `from browser_use import Agent, Browser, ChatGoogle`
- `Browser(cloud_profile_id=..., cloud_proxy_country_code="us")` → `Browser(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', user_data_dir='~/Library/Application Support/Google/Chrome', profile_directory='Default')`
- `ChatBrowserUse()` → `ChatGoogle(model='gemini-2.0-flash')`
- Agent task: reference `os.path.abspath(filepath)` instead of `cloud_filename`
- Remove explicit `browser.start()` call (Agent.run() handles this automatically)
- Keep `browser.kill()` in finally block

Result: ~25 lines down from ~96.

### 2. `pyproject.toml` — Add dependency
Add `google-genai>=1.0.0` (required by `ChatGoogle`).

### 3. `.env.example` — Update env vars
Remove `BROWSER_USE_API_KEY` and `BROWSER_USE_PROFILE_ID`. Add `GEMINI_API_KEY=your-gemini-api-key`.

### 4. `.env` — Clean up
Remove the two `BROWSER_USE_*` entries. Keep `GEMINI_API_KEY`.

### 5. `CLAUDE.md` — Update docs
Reflect local Chrome architecture: no cloud, no presigned URLs, local file access, `ChatGoogle` LLM. Add note that Chrome must be closed before running.

### 6. `main.py` — No changes
The `post_to_x(filepath, caption)` signature is unchanged.

## Important Notes
- **Chrome must be fully closed** before running — browser-use needs exclusive profile access
- browser-use auto-copies the Chrome profile to a temp dir, so the real profile is never corrupted
- `GEMINI_API_KEY` is auto-detected by `google.genai` from the environment — no explicit `api_key=` param needed
- Video files (`.mp4`, `.mov`) can now potentially work since there's no cloud API limitation, though X's web UI has its own constraints

## Verification
1. Run `uv sync` to install new dependency
2. Close Chrome completely
3. Run `uv run main.py <test-image> "test caption"` and verify:
   - Chrome launches with the correct profile
   - Agent navigates to x.com (already logged in)
   - Post is composed with caption and media attached
   - Post is published successfully
