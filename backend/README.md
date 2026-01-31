# ragebAIt Backend

AI Sports Miscommentary Generator - Turn any sports clip into viral ragebait comedy gold.

## 🔥 NEW: Clip-Based Ragebait Workflow

The API now automatically:
1. **Analyzes** your 1-2 minute video to find the funniest moments
2. **Extracts** the best 10-15 second clip
3. **Generates** fast, angry ragebait commentary (TikTok style)
4. **Uses fal.ai TTS** with angry emotion and 1.2x speed for that viral feel

## Quick Start

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
FAL_KEY=your_fal_ai_key_here  # For TTS

# Optional (for full functionality)
VERCEL_BLOB_TOKEN=your_vercel_blob_token

# Development
DEBUG=true
MOCK_MODE=false
```

### 3. Run the Server

```bash
uvicorn backend.main:app --reload
```

Server will start at http://localhost:8000

### 4. Test the API

```bash
# Basic tests
python backend/test_api.py

# Full test with video
python backend/test_api.py /path/to/sports_video.mp4
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/lenses` | List available comedy lenses |
| POST | `/api/generate` | **Generate ragebait clip from video** |
| GET | `/api/video/{id}` | Get video info |

### Meme Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meme/options` | Get meme options for video |
| POST | `/api/meme/generate` | Generate meme image |
| GET | `/api/meme/templates` | List meme templates |

## Generate Ragebait Clip

Upload a 1-2 minute video, get back a 10-15 second viral-ready clip:

```bash
curl -X POST http://localhost:8000/api/generate \
  -F "video=@sports_clip.mp4" \
  -F "lens=nature_documentary" \
  -F "clip_duration_min=10" \
  -F "clip_duration_max=15"
```

Response:
```json
{
  "video_id": "abc123",
  "video_url": "https://...",
  "thumbnail_url": "https://...",
  "commentary_segments": [
    {
      "start_time": 0.0,
      "end_time": 3.5,
      "text": "BRO WAIT- Look at this guy!",
      "emotion": "excited"
    },
    {
      "start_time": 3.5,
      "end_time": 7.0,
      "text": "NO WAY HE JUST DID THAT! THIS IS INSANE!",
      "emotion": "tense"
    }
  ],
  "lens": "nature_documentary",
  "duration": 12.5
}
```

### What Happens Behind the Scenes

1. **Funny Moment Detection**: Gemini analyzes your full video and finds the TOP 3 funniest/most viral-worthy moments
2. **Clip Extraction**: The best moment (highest humor score) is extracted as a 10-15 second clip
3. **Ragebait Commentary**: Short, punchy, fast commentary is generated (TikTok style)
4. **fal.ai TTS**: Voice synthesis with angry emotion and 1.2x speed
5. **Final Output**: Original audio (lowered) + commentary merged into final clip

## Available Lenses

| ID | Name | Style |
|----|------|-------|
| `nature_documentary` | 🦁 Nature Documentary | David Attenborough observing wildlife |
| `heist_movie` | 🎬 Heist Movie | Tense thriller narrator |
| `alien_anthropologist` | 👽 Alien Anthropologist | Confused alien studying humans |
| `cooking_show` | 👨‍🍳 Cooking Show | Enthusiastic chef |
| `shakespearean` | 🎭 Shakespearean | Dramatic tragedy |
| `corporate_meeting` | 💼 Corporate Meeting | Business jargon |
| `true_crime` | 🎙️ True Crime | Suspenseful podcast |

All lenses now generate **ragebait-style** commentary optimized for short-form viral content!

## Architecture

```
backend/
├── main.py              # FastAPI app
├── config.py            # Environment config
├── models/
│   └── schemas.py       # Pydantic models
├── routers/
│   ├── generate.py      # Video generation (NEW: clip-based workflow)
│   └── meme.py          # Meme generation
├── services/
│   ├── video_processor.py  # OpenCV/moviepy (NEW: clip extraction)
│   ├── gemini_client.py    # Gemini API (NEW: funny moment detection)
│   ├── tts_client.py       # fal.ai TTS (UPDATED: ragebait voice)
│   ├── storage_client.py   # Vercel Blob
│   └── meme_engine.py      # Meme rendering
└── prompts/
    └── lenses.py        # Comedy lens prompts
```

## Team Integration

### For Vatsala (Frontend)

Base URL: `http://localhost:8000`

```typescript
// Generate ragebait clip from longer video
const formData = new FormData();
formData.append('video', file);  // 1-2 minute video
formData.append('lens', 'nature_documentary');
formData.append('clip_duration_min', '10');
formData.append('clip_duration_max', '15');

const response = await fetch('/api/generate', {
  method: 'POST',
  body: formData
});

// Response includes the extracted viral clip
const { 
  video_id, 
  video_url,  // URL to final 10-15s clip with commentary
  commentary_segments,
  duration  // Duration of extracted clip
} = await response.json();

// Get more info about what was detected
const videoInfo = await fetch(`/api/video/${video_id}`);
const { funny_moment } = await videoInfo.json();
// funny_moment contains: description, humor_score, reason
```

### For Sanskar (Browser Use)

Add context to generation:

```python
context = {
    "teams": "Lakers vs Celtics",
    "players": "LeBron James, Jayson Tatum",
    "recent_news": "Lakers on 5-game win streak"
}

response = requests.post('/api/generate', 
    files={'video': video_file},
    data={
        'lens': 'nature_documentary',
        'context': json.dumps(context),
        'clip_duration_min': 10,
        'clip_duration_max': 15
    }
)
```

### For Dizzy (Nano Banana)

Implement endpoint in `routers/meme.py`:

```python
# In _try_nano_banana function, set:
NANO_BANANA_URL = "https://your-nano-banana-api.com/generate"

# Expected request format:
{
    "image_base64": "...",
    "top_text": "TOP TEXT",
    "bottom_text": "BOTTOM TEXT",
    "style": "classic",
    "format": "square"
}

# Expected response:
{
    "image_url": "https://..."
}
```

## Troubleshooting

### TTS Not Working

Make sure you have the fal.ai API key:
```bash
export FAL_KEY=your_fal_ai_key_here
```

Or enable mock mode to skip TTS:
```bash
MOCK_MODE=true
```

### Gemini Rate Limits

If you hit rate limits, the API will retry automatically. For heavy usage, consider:
- Reducing video duration
- Adding delays between requests

### Storage Issues

If Vercel Blob is not configured, files are saved locally in `/tmp/ragebait/`.

## fal.ai TTS Voice Settings

The TTS uses fal.ai's minimax/speech-02-hd with these ragebait-optimized settings:

```python
{
    "voice_id": "Male-01",
    "speed": 1.2,      # TikTok speed
    "vol": 1.0,
    "pitch": 0,
    "emotion": "angry" # Ragebait energy!
}
```

Different lenses may use different emotions:
- `heist_movie`: angry + 1.3x speed (extra tension)
- `cooking_show`: happy + 1.25x speed (enthusiastic)
- `true_crime`: angry + 1.0x speed (slower for suspense)
