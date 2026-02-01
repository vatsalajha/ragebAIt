"""
ragebAIt - Parody Generation Router
Handles image-to-video generations using fal.ai.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.parody_service import parody_service
from backend.services.storage_client import storage_client
from backend.routers.generate import get_video_data
from backend.config import settings

router = APIRouter(tags=["parody"])

class ParodyGenerateRequest(BaseModel):
    """Request to generate a parody video from a video frame or meme."""
    video_id: str = Field(..., description="Video ID to get context/frame from")
    frame_index: Optional[int] = Field(default=None, description="Specific frame index")
    motion_directive: str = Field(..., description="Motion instruction (e.g. 'slow zoom-in')")
    meme_url: Optional[str] = Field(default=None, description="Optional URL of a generated meme to use instead of a raw frame")

class ParodyGenerateResponse(BaseModel):
    """Response with generated parody video."""
    parody_id: str = Field(..., description="Unique parody ID")
    video_url: str = Field(..., description="URL to generated parody video")
    motion_directive: str = Field(..., description="The motion directive used")

@router.post(
    "/api/parody/generate",
    response_model=ParodyGenerateResponse,
    summary="Generate an image-to-video parody using fal.ai"
)
async def generate_parody(request: ParodyGenerateRequest):
    """
    Generate an AI parody video using fal.ai image-to-video.
    """
    if not parody_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Parody service (fal.ai) not available. Check FAL_KEY."
        )

    # 1. Determine the source image
    source_image_url = request.meme_url
    
    if not source_image_url:
        # Fallback to frame from video
        video_data = get_video_data(request.video_id)
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        frames = video_data.get("frames", [])
        if not frames:
            raise HTTPException(status_code=404, detail="No frames available for this video")
        
        # Select frame
        if request.frame_index is not None:
            if request.frame_index < 0 or request.frame_index >= len(frames):
                raise HTTPException(status_code=400, detail=f"Frame index out of range")
            frame = frames[request.frame_index]
        else:
            frame = frames[len(frames) // 2]
        
        # We need a URL. If it's base64, we might need to upload it temporarily or use data URI.
        # fal.ai supports data URIs.
        source_image_url = f"data:image/jpeg;base64,{frame['image_base64']}"

    # 2. Prepare the prompt
    # We can use the commentary as context if we have it
    video_data = get_video_data(request.video_id)
    commentary = ""
    if video_data:
        commentary = video_data.get("commentary_text", "")
    
    prompt = f"A parody of a sports moment. {commentary[:500]}"
    
    try:
        parody_id = uuid.uuid4().hex[:12]
        
        video_url = await parody_service.generate_image_to_video(
            image_url=source_image_url,
            prompt=prompt,
            motion_directive=request.motion_directive
        )
        
        return ParodyGenerateResponse(
            parody_id=parody_id,
            video_url=video_url,
            motion_directive=request.motion_directive
        )
        
    except Exception as e:
        print(f"[Parody] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
