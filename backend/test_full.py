"""
ragebAIt - Full End-to-End API Test Script
Tests:
1. Video Generation (clip extraction + commentary + TTS)
2. Status Polling (verify meme/caption are returned)
3. Meme Regeneration
4. Parody Generation
"""

import asyncio
import httpx
import sys
import os
import base64
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_VIDEO = "/Users/vatsalajha/hack/ragebAIt/backend/media/test_video.mp4" # Assuming this exists or using a sample
TEST_IMAGE = "/Users/vatsalajha/hack/ragebAIt/test_image.jpg"

async def test_full_flow():
    print("=" * 60)
    print("🚀 Starting Full End-to-End API Test")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=600.0) as client:
        # 1. Health check
        print("\n🔍 Step 1: Health Check")
        resp = await client.get(f"{BASE_URL}/api/health")
        print(f"   Status: {resp.status_code}, Services: {resp.json()['services']}")

        # 2. Upload Video and Generate
        print("\n🎬 Step 2: Generating Ragebait Clip")
        if not os.path.exists(TEST_VIDEO):
            print(f"   ❌ Test video not found at {TEST_VIDEO}")
            return

        with open(TEST_VIDEO, 'rb') as f:
            files = {'video': (Path(TEST_VIDEO).name, f, 'video/mp4')}
            data = {'lens': 'nature_documentary'}
            resp = await client.post(f"{BASE_URL}/api/generate", files=files, data=data)
        
        if resp.status_code != 200:
            print(f"   ❌ Generation failed: {resp.text}")
            return
        
        result = resp.json()
        video_id = result['video_id']
        print(f"   ✅ Clip ready! Video ID: {video_id}")
        print(f"   Video URL: {result.get('video_url')}")

        # 3. Test Status Polling (Check for auto-meme)
        print("\n⏳ Step 3: Polling for Status (should have meme/caption)")
        # Wait a few seconds for auto-meme
        await asyncio.sleep(5)
        resp = await client.get(f"{BASE_URL}/api/video/{video_id}")
        status_data = resp.json()
        print(f"   Meme URL: {status_data.get('meme_url')}")
        print(f"   Caption: {status_data.get('caption')}")
        
        if status_data.get('meme_url'):
            print("   ✅ Auto-meme retrieval successful")
        else:
            print("   ⚠️ Auto-meme not found in status yet (might still be generating)")

        # 4. Test Meme Regeneration
        print("\n🍌 Step 4: Testing Meme Regeneration")
        resp = await client.post(f"{BASE_URL}/api/meme/generate", json={"video_id": video_id})
        if resp.status_code == 200:
            meme_data = resp.json()
            print(f"   ✅ Regrown Meme URL: {meme_data['meme_url']}")
        else:
            print(f"   ❌ Meme regen failed: {resp.text}")

        # 5. Test Parody Generation
        print("\n🎬 Step 5: Testing Parody Generation (fal.ai)")
        parody_request = {
            "video_id": video_id,
            "motion_directive": "slow zoom-in, stadium lights flicker slightly",
            "meme_url": status_data.get('meme_url') or "https://picsum.photos/400/400"
        }
        resp = await client.post(f"{BASE_URL}/api/parody/generate", json=parody_request)
        if resp.status_code == 200:
            parody_data = resp.json()
            print(f"   ✅ Parody URL: {parody_data['video_url']}")
        else:
            print(f"   ❌ Parody generation failed: {resp.text}")

    print("\n" + "=" * 60)
    print("🏁 Full Flow Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    if not os.path.exists(TEST_VIDEO):
        # Create a dummy video if it doesn't exist for test purposes? 
        # Better to use a real one. Let's look for any mp4 in backend/media
        import glob
        existing_videos = glob.glob("/Users/vatsalajha/hack/ragebAIt/backend/media/*.mp4")
        if existing_videos:
            TEST_VIDEO = existing_videos[0]
            print(f"Using existing video: {TEST_VIDEO}")
        else:
            # Attempting to use the one from previous session if I can guess path
            TEST_VIDEO = "/Users/vatsalajha/hack/ragebAIt/test_video.mp4"

    asyncio.run(test_full_flow())
