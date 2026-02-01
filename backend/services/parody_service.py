"""
ragebAIt - Parody Generation Service
Handles image-to-video generation using fal.ai.
"""

import os
import requests
from typing import Optional
from backend.config import settings

# fal_client reads FAL_KEY from environment
if os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = os.getenv("FAL_KEY", "").strip()

import fal_client

class ParodyService:
    """Service for generating parody videos using fal.ai Image-to-Video models."""
    
    def __init__(self):
        self.fal_key = os.getenv("FAL_KEY", "").strip()
        self._available = bool(self.fal_key)
        
        if self._available:
            print("[Parody] fal.ai parody service initialized")
        else:
            print("[Parody] Warning: FAL_KEY not set. Parody features disabled.")

    def is_available(self) -> bool:
        """Check if parody service is available."""
        return self._available

    async def generate_image_to_video(
        self,
        image_url: str,
        prompt: str,
        motion_directive: Optional[str] = None,
        model: str = "fal-ai/minimax-video/image-to-video"
    ) -> str:
        """
        Generate a video from an image using fal.ai.
        
        Args:
            image_url: URL to the source image (or data URI)
            prompt: Base prompt for generation
            motion_directive: Optional motion instruction (e.g. "slow zoom-in")
            model: fal.ai model ID
            
        Returns:
            URL to the generated video
        """
        if not self._available:
            raise RuntimeError("Parody service not available - FAL_KEY not set")

        full_prompt = prompt
        if motion_directive:
            full_prompt = f"{prompt}, {motion_directive}"

        print(f"[Parody] Generating video from image using {model}")
        print(f"[Parody] Prompt: {full_prompt}")

        try:
            # Using subscribe to handle wait
            handler = await fal_client.subscribe_async(
                model,
                arguments={
                    "prompt": full_prompt,
                    "image_url": image_url
                },
            )
            
            result = handler
            if result and "video" in result:
                video_url = result["video"]["url"]
                print(f"[Parody] Generated video URL: {video_url}")
                return video_url
            else:
                raise RuntimeError(f"fal.ai parody generation failed: {result}")

        except Exception as e:
            print(f"[Parody] Error generating parody: {e}")
            raise

# Singleton instance
parody_service = ParodyService()
