"""
ragebAIt - API Test Script

Run this to test the backend endpoints locally.
"""

import asyncio
import httpx
import sys
from pathlib import Path


BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health endpoint."""
    print("\n🔍 Testing /api/health...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200


async def test_lenses():
    """Test lenses endpoint."""
    print("\n🎭 Testing /api/lenses...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/lenses")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Available lenses: {len(data.get('lenses', []))}")
        for lens in data.get('lenses', []):
            print(f"      - {lens['emoji']} {lens['name']} ({lens['id']})")
        return response.status_code == 200


async def test_meme_templates():
    """Test meme templates/styles endpoint."""
    print("\n📋 Testing /api/meme/templates...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/meme/templates")
        print(f"   Status: {response.status_code}")
        data = response.json()
        for template in data.get('templates', []):
            print(f"      - {template['name']}: {template['description']}")
    
    print("\n🎨 Testing /api/meme/styles...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/meme/styles")
        print(f"   Status: {response.status_code}")
        data = response.json()
        for style in data.get('styles', []):
            print(f"      - {style['name']}: {style['description'][:50]}...")
        return response.status_code == 200


async def test_generate_video(video_path: str, lens: str = "nature_documentary"):
    """Test video generation endpoint with new ragebait workflow."""
    print(f"\n🎬 Testing /api/generate with {lens} lens...")
    print(f"   Video: {video_path}")
    
    if not Path(video_path).exists():
        print(f"   ❌ Video file not found: {video_path}")
        return False
    
    # Longer timeout for new workflow: analyze video -> find moments -> extract clip -> commentary -> TTS
    async with httpx.AsyncClient(timeout=600.0) as client:  # 10 minute timeout
        with open(video_path, 'rb') as f:
            files = {'video': (Path(video_path).name, f, 'video/mp4')}
            data = {
                'lens': lens,
                'min_scene_duration': '8',
                'max_scene_duration': '30'
            }
            
            print("   🔍 Step 1: Finding complete funny SCENES in video...")
            print("   ✂️ Step 2: Extracting complete scene (waits for action to finish)...")
            print("   🎙️ Step 3: Generating ragebait commentary...")
            print("   🔊 Step 4: Synthesizing TTS with fal.ai...")
            print("   (This may take 2-5 minutes for longer videos)")
            response = await client.post(
                f"{BASE_URL}/api/generate",
                files=files,
                data=data
            )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n   ✅ Ragebait clip generated!")
            print(f"   Video ID: {result.get('video_id')}")
            print(f"   Output URL: {result.get('video_url')}")
            print(f"   Clip Duration: {result.get('duration')}s (extracted from longer video)")
            print(f"   Commentary Segments: {len(result.get('commentary_segments', []))}")
            
            print(f"\n   📝 Generated Commentary:")
            for i, seg in enumerate(result.get('commentary_segments', [])):
                print(f"      [{seg['start_time']:.1f}s-{seg['end_time']:.1f}s] {seg['text']}")
            
            return result.get('video_id')
        else:
            print(f"   ❌ Error: {response.text}")
            return None


async def test_meme_generate(video_id: str):
    """Test Nano Banana meme generation endpoint."""
    print(f"\n🍌 Testing /api/meme/generate with Nano Banana for video {video_id}...")
    print("   (This uses Gemini's native image generation - may take 30-60 seconds)")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/meme/generate",
            json={
                "video_id": video_id
            }
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n   ✅ Meme generated!")
            print(f"   Meme ID: {result.get('meme_id')}")
            print(f"   Meme URL: {result.get('meme_url')}")
            print(f"   Style: {result.get('style')}")
            print(f"   Caption: {result.get('caption')}")
            print(f"   Prompt: {result.get('image_prompt', '')[:100]}...")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False


async def run_all_tests(video_path: str = None):
    """Run all tests."""
    print("=" * 60)
    print("🧪 ragebAIt API Test Suite")
    print("=" * 60)
    
    # Test basic endpoints
    health_ok = await test_health()
    lenses_ok = await test_lenses()
    templates_ok = await test_meme_templates()
    
    if not health_ok:
        print("\n❌ Health check failed - is the server running?")
        print("   Start with: uvicorn main:app --reload")
        return
    
    # Test video generation if video provided
    if video_path:
        video_id = await test_generate_video(video_path, "nature_documentary")
        
        if video_id:
            # Test Nano Banana meme generation
            await test_meme_generate(video_id)
    else:
        print("\n💡 To test video generation, provide a video path:")
        print("   python test_api.py /path/to/sports_video.mp4")
    
    print("\n" + "=" * 60)
    print("✅ Basic tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_all_tests(video_path))
