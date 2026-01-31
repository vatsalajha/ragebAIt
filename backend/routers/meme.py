"""
ragebAIt - Meme Generation Router
Handles meme options and generation.
"""

import uuid
import httpx
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.models.schemas import (
    MemeOptionsResponse,
    MemeGenerateRequest,
    MemeGenerateResponse,
    MemeCaption,
    MemeFormat,
    LensType,
    ErrorResponse
)
from backend.services.gemini_client import gemini_client
from backend.services.meme_engine import meme_engine
from backend.services.storage_client import storage_client
from backend.routers.generate import get_video_data


router = APIRouter(tags=["meme"])


@router.get(
    "/api/meme/options",
    response_model=MemeOptionsResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_meme_options(
    video_id: str,
    lens: Optional[LensType] = None
):
    """
    Get meme generation options for a processed video.
    
    Returns:
    - Best frame selected by AI
    - 3 caption options matching the lens style
    """
    # Get video data from store
    video_data = get_video_data(video_id)
    if not video_data:
        raise HTTPException(status_code=404, detail="Video not found. Generate video first.")
    
    frames = video_data.get("frames", [])
    if not frames:
        raise HTTPException(status_code=404, detail="No frames available for this video")
    
    commentary_text = video_data.get("commentary_text", "")
    video_lens = lens or video_data.get("lens", LensType.NATURE_DOCUMENTARY)
    
    try:
        # Select best frame using Gemini
        best_frame_result = await gemini_client.select_best_frame_for_meme(
            frames,
            commentary_text
        )
        
        best_frame_index = best_frame_result.get("best_frame_index", 0)
        best_frame_index = min(best_frame_index, len(frames) - 1)
        best_frame = frames[best_frame_index]
        
        # Generate caption options
        captions_data = await gemini_client.generate_meme_captions(
            best_frame["image_base64"],
            commentary_text,
            video_lens
        )
        
        # Convert to MemeCaption objects
        captions = []
        for i, cap_data in enumerate(captions_data[:3]):
            captions.append(MemeCaption(
                id=cap_data.get("id", f"caption_{i}"),
                top_text=cap_data.get("top_text"),
                bottom_text=cap_data.get("bottom_text"),
                caption=cap_data.get("caption"),
                template=cap_data.get("template", "classic"),
                humor_rating=cap_data.get("humor_rating", 7)
            ))
        
        return MemeOptionsResponse(
            video_id=video_id,
            frame_base64=best_frame["image_base64"],
            frame_timestamp=best_frame["timestamp"],
            frame_reason=best_frame_result.get("reason", "AI selected best frame"),
            captions=captions,
            lens=video_lens
        )
        
    except Exception as e:
        print(f"[Meme] Error getting options: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/api/meme/generate",
    response_model=MemeGenerateResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def generate_meme(request: MemeGenerateRequest):
    """
    Generate a meme image from the selected frame and caption.
    
    Supports:
    - Classic meme format (Impact font top/bottom)
    - Modern meme format (white bar with caption)
    - Quote format (text overlay on image)
    
    Can optionally use Dizzy's Nano Banana API for enhanced generation.
    """
    # Get video data
    video_data = get_video_data(request.video_id)
    if not video_data:
        raise HTTPException(status_code=404, detail="Video not found")
    
    frames = video_data.get("frames", [])
    if not frames:
        raise HTTPException(status_code=404, detail="No frames available")
    
    # Use first frame or find the previously selected one
    frame_base64 = frames[0]["image_base64"]
    
    meme_id = uuid.uuid4().hex[:12]
    
    try:
        # Option 1: Try Nano Banana API (Dizzy's integration)
        if request.use_nano_banana:
            meme_url = await _try_nano_banana(
                frame_base64,
                request.caption,
                request.format
            )
            if meme_url:
                # Get dimensions from format
                dimensions = {
                    MemeFormat.SQUARE: (1080, 1080),
                    MemeFormat.WIDE: (1200, 675),
                    MemeFormat.TALL: (1080, 1920),
                }
                width, height = dimensions.get(request.format, (1080, 1080))
                
                return MemeGenerateResponse(
                    meme_id=meme_id,
                    meme_url=meme_url,
                    format=request.format,
                    width=width,
                    height=height
                )
        
        # Option 2: Use local meme engine
        meme_bytes = meme_engine.render_meme(
            frame_base64,
            request.caption,
            request.format
        )
        
        # Upload to storage
        if storage_client.is_available():
            meme_url = await storage_client.upload_image(
                meme_bytes,
                f"meme_{meme_id}.png"
            )
        else:
            # Save locally and return file path
            output_path = settings.TEMP_DIR / f"meme_{meme_id}.png"
            with open(output_path, 'wb') as f:
                f.write(meme_bytes)
            meme_url = f"file://{output_path}"
        
        # Get dimensions
        dimensions = {
            MemeFormat.SQUARE: (1080, 1080),
            MemeFormat.WIDE: (1200, 675),
            MemeFormat.TALL: (1080, 1920),
        }
        width, height = dimensions.get(request.format, (1080, 1080))
        
        return MemeGenerateResponse(
            meme_id=meme_id,
            meme_url=meme_url,
            format=request.format,
            width=width,
            height=height
        )
        
    except Exception as e:
        print(f"[Meme] Error generating: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def _try_nano_banana(
    frame_base64: str,
    caption: MemeCaption,
    format: MemeFormat
) -> Optional[str]:
    """
    Try to generate meme using Dizzy's Nano Banana API.
    
    This is a placeholder - Dizzy will provide the actual endpoint.
    
    Args:
        frame_base64: Base64 encoded frame image
        caption: Caption configuration
        format: Output format
        
    Returns:
        URL to generated meme, or None if API unavailable
    """
    # TODO: Dizzy to implement Nano Banana integration
    # Expected endpoint: POST /api/nano-banana/generate
    # 
    # Example request:
    # {
    #     "image_base64": "...",
    #     "top_text": "TOP TEXT",
    #     "bottom_text": "BOTTOM TEXT",
    #     "style": "classic|modern|quote",
    #     "format": "square|wide|tall"
    # }
    #
    # Example response:
    # {
    #     "image_url": "https://..."
    # }
    
    NANO_BANANA_URL = None  # Set by Dizzy
    
    if not NANO_BANANA_URL:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                NANO_BANANA_URL,
                json={
                    "image_base64": frame_base64,
                    "top_text": caption.top_text,
                    "bottom_text": caption.bottom_text,
                    "caption": caption.caption,
                    "style": caption.template,
                    "format": format.value
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("image_url")
    except Exception as e:
        print(f"[Meme] Nano Banana API error: {e}")
    
    return None


@router.get("/api/meme/templates")
async def list_meme_templates():
    """List available meme templates."""
    return {
        "templates": [
            {
                "id": "classic",
                "name": "Classic Meme",
                "description": "Impact font, top and bottom text",
                "example": "TOP TEXT / BOTTOM TEXT"
            },
            {
                "id": "modern",
                "name": "Modern Caption",
                "description": "White bar at top with caption",
                "example": "Nobody: ... Me:"
            },
            {
                "id": "quote",
                "name": "Quote Overlay",
                "description": "Text overlay on darkened bottom",
                "example": "\"Inspirational quote\" - Person"
            }
        ]
    }
