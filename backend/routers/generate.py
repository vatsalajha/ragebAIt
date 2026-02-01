"""
ragebAIt - Video Generation Router
Handles video upload, funny moment detection, clip extraction, and ragebait commentary generation.
"""

import uuid
import tempfile
import aiofiles
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.config import settings
from backend.models.schemas import (
    GenerateResponse,
    CommentarySegment,
    LensType,
    ErrorResponse
)
from backend.services.video_processor import video_processor
from backend.services.gemini_client import gemini_client
from backend.services.tts_client import tts_client
from backend.services.storage_client import storage_client


router = APIRouter(tags=["generation"])


# In-memory store for video data (for meme generation later)
# In production, use Redis or database
video_store: dict[str, dict] = {}


@router.post(
    "/api/generate",
    response_model=GenerateResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def generate_commentary(
    video: UploadFile = File(..., description="Video file to process (1-2 minutes)"),
    lens: LensType = Form(..., description="Comedy lens to apply"),
    context: Optional[str] = Form(default=None, description="JSON context from Browser Use"),
    min_scene_duration: float = Form(default=8.0, description="Minimum scene duration (seconds)"),
    max_scene_duration: float = Form(default=30.0, description="Maximum scene duration (seconds)")
):
    """
    Generate AI ragebait comedy commentary for a sports video.
    
    SCENE-BASED WORKFLOW:
    1. Accepts a longer video file (1-2 minutes)
    2. Uses Gemini to FIND the funniest COMPLETE SCENE (waits for action to finish)
    3. Extracts that complete scene
    4. Generates ragebait-style commentary for the scene
    5. Uses fal.ai TTS with angry/fast voice (TikTok style)
    6. Returns the final viral-ready clip with the complete scene
    """
    # Validate file
    if not video.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = Path(video.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_VIDEO_EXTENSIONS}"
        )
    
    # Generate unique ID for this generation
    video_id = uuid.uuid4().hex[:12]
    
    try:
        # Save uploaded video to temp file
        temp_video_path = settings.TEMP_DIR / f"{video_id}_input{file_ext}"
        
        async with aiofiles.open(temp_video_path, 'wb') as f:
            content = await video.read()
            await f.write(content)
        
        print(f"[Generate] Saved video to {temp_video_path}")
        
        # Get video info
        video_info = video_processor.get_video_info(str(temp_video_path))
        print(f"[Generate] Video info: {video_info}")
        
        # Check duration limit
        if video_info['duration'] > settings.MAX_VIDEO_DURATION_SECONDS:
            raise HTTPException(
                status_code=400,
                detail=f"Video too long. Max duration: {settings.MAX_VIDEO_DURATION_SECONDS}s"
            )
        
        # Parse context if provided
        context_dict = None
        if context:
            import json
            try:
                context_dict = json.loads(context)
            except json.JSONDecodeError:
                pass  # Ignore invalid context
        
        # STEP 1: Find complete funny scenes in the video
        print(f"[Generate] 🔍 Finding complete funny scenes in {video_info['duration']:.1f}s video...")
        funny_moments = await gemini_client.find_funny_moments(
            str(temp_video_path),
            video_duration=video_info['duration'],
            min_clip_duration=min_scene_duration,
            max_clip_duration=max_scene_duration,
            num_moments=3  # Find top 3, use the best one
        )
        
        if not funny_moments:
            raise HTTPException(
                status_code=500,
                detail="Could not find any interesting scenes in the video"
            )
        
        # Use the best scene (highest humor score)
        best_moment = funny_moments[0]
        scene_duration = best_moment.end_time - best_moment.start_time
        print(f"[Generate] 🎯 Best scene: [{best_moment.start_time:.1f}s-{best_moment.end_time:.1f}s] ({scene_duration:.1f}s) Score: {best_moment.humor_score}/10")
        print(f"[Generate]    Description: {best_moment.description}")
        print(f"[Generate]    Reason: {best_moment.reason}")
        
        # STEP 2: Extract the complete scene
        clip_path = str(settings.TEMP_DIR / f"{video_id}_clip.mp4")
        clip_path = video_processor.extract_clip(
            str(temp_video_path),
            start_time=best_moment.start_time,
            end_time=best_moment.end_time,
            output_path=clip_path
        )
        
        clip_duration = best_moment.end_time - best_moment.start_time
        print(f"[Generate] ✂️ Extracted {clip_duration:.1f}s clip")
        
        # STEP 3: Generate ragebait commentary for the clip
        print(f"[Generate] 🎙️ Generating ragebait commentary with {lens.value} lens...")
        segments = await gemini_client.generate_ragebait_commentary(
            clip_path,
            moment=best_moment,
            lens=lens,
            context=context_dict
        )
        
        print(f"[Generate] Got {len(segments)} ragebait commentary segments")
        
        # Store initial video data (without meme yet)
        commentary_text = " ".join([s.text for s in segments])
        video_store[video_id] = {
            "video_path": clip_path,
            "original_video_path": str(temp_video_path),
            "segments": segments,
            "commentary_text": commentary_text,
            "lens": lens,
            "video_info": {
                "duration": clip_duration,
                "original_duration": video_info['duration'],
                **video_info
            }
        }
        
        # Extract frames from clip for meme generation later
        frames = video_processor.extract_frames(
            clip_path,
            fps=1.0,
            max_frames=int(clip_duration) + 1
        )
        
        # STEP 4: Generate TTS audio with fal.ai (ragebait style)
        output_video_url = ""
        thumbnail_url = None
        
        if tts_client.is_available():
            audio_path = await tts_client.synthesize_commentary(
                segments,
                lens,
                output_path=str(settings.TEMP_DIR / f"{video_id}_audio.mp3")
            )
            
            # STEP 5: Merge audio with clip
            output_video_path = video_processor.merge_audio_video(
                clip_path,
                audio_path,
                output_path=str(settings.TEMP_DIR / f"{video_id}_output.mp4"),
                keep_original_audio=True,
                original_audio_volume=0.15  # Lower original audio for ragebait
            )
            
            # Create thumbnail
            thumb_path = video_processor.create_thumbnail(
                output_video_path,
                timestamp=clip_duration * 0.5  # Middle of clip
            )
            
            # Upload to storage
            if storage_client.is_available():
                output_video_url = await storage_client.upload_from_path(output_video_path)
                thumbnail_url = await storage_client.upload_from_path(thumb_path)
                print(f"[Generate] ☁️ Uploaded to storage: {output_video_url}")
            else:
                output_video_url = f"file://{output_video_path}"
        else:
            # TTS not available - return clip without audio
            if storage_client.is_available():
                output_video_url = await storage_client.upload_from_path(clip_path)
            else:
                output_video_url = f"file://{clip_path}"
        
        # Update storage URLs
        video_store[video_id].update({
            "output_url": output_video_url,
            "thumbnail_url": thumbnail_url,
            "frames": frames,
            "funny_moment": {
                "start_time": best_moment.start_time,
                "end_time": best_moment.end_time,
                "description": best_moment.description,
                "humor_score": best_moment.humor_score,
                "reason": best_moment.reason
            }
        })

        # STEP 6: Auto-generate meme in background (simulated here for simplicity)
        # In a real app, this should be a background task
        try:
            print(f"[Generate] 🍌 Auto-generating meme...")
            meme_result = await meme_engine.generate_meme(
                frame_base64=frames[len(frames) // 2]["image_base64"],
                context=commentary_text
            )
            video_store[video_id].update({
                "meme_url": await storage_client.upload_image(base64.b64decode(meme_result["image_base64"]), "meme.png") if storage_client.is_available() else f"data:image/png;base64,{meme_result['image_base64']}",
                "caption": meme_result["caption"]
            })
            print(f"[Generate] ✅ Auto-meme ready")
        except Exception as e:
            print(f"[Generate] Warning: Auto-meme failed: {e}")
        
        print(f"[Generate] ✅ Ragebait clip ready! Video ID: {video_id}")
        
        return GenerateResponse(
            video_id=video_id,
            video_url=output_video_url,
            thumbnail_url=thumbnail_url,
            commentary_segments=segments,
            lens=lens,
            duration=clip_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Generate] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/lenses")
async def list_lenses():
    """List all available comedy lenses."""
    from backend.prompts.lenses import LENSES
    
    return {
        "lenses": [
            {
                "id": lens_id,
                "name": config.name,
                "emoji": config.emoji,
            }
            for lens_id, config in LENSES.items()
        ]
    }


@router.get("/api/video/{video_id}")
async def get_video_info(video_id: str):
    """Get info about a generated video."""
    if video_id not in video_store:
        raise HTTPException(status_code=404, detail="Video not found")
    
    data = video_store[video_id]
    return {
        "video_id": video_id,
        "video_url": data.get("output_url", ""),
        "thumbnail_url": data.get("thumbnail_url"),
        "meme_url": data.get("meme_url"),
        "caption": data.get("caption"),
        "lens": data.get("lens", ""),
        "duration": data.get("video_info", {}).get("duration", 0),
        "original_duration": data.get("video_info", {}).get("original_duration", 0),
        "segments": data.get("segments", []),
        "funny_moment": data.get("funny_moment", {}),
    }


def get_video_data(video_id: str) -> Optional[dict]:
    """Get stored video data (for meme router)."""
    return video_store.get(video_id)
