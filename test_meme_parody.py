import asyncio
import os
import base64
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.services.meme_engine import meme_engine
from backend.services.parody_service import parody_service
from backend.config import settings

async def test_meme():
    print("--- Testing Meme Engine ---")
    if not meme_engine.is_available():
        print("Meme engine not available")
        return

    # Use the downloaded test image
    with open("test_image.jpg", "rb") as f:
        image_bytes = f.read()
        image_base_64 = base64.b64encode(image_bytes).decode('utf-8')
    
    try:
        result = await meme_engine.generate_meme(
            frame_base64=image_base_64,
            context="A funny sports moment"
        )
        print("Meme generated successfully!")
        print(f"Caption: {result['caption']}")
    except Exception as e:
        print(f"Meme generation failed: {e}")
        import traceback
        traceback.print_exc()

async def test_parody():
    print("\n--- Testing Parody Service ---")
    if not parody_service.is_available():
        print("Parody service not available")
        return

    image_url = "https://picsum.photos/800/600"
    prompt = "A funny parody of a piano playing itself"
    
    try:
        video_url = await parody_service.generate_image_to_video(
            image_url=image_url,
            prompt=prompt,
            motion_directive="slow zoom-in"
        )
        print(f"Parody generated successfully: {video_url}")
    except Exception as e:
        print(f"Parody generation failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_meme()
    await test_parody()

if __name__ == "__main__":
    asyncio.run(main())
