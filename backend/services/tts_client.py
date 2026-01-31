"""
ragebAIt - Text-to-Speech Client
Handles voice synthesis using fal.ai's minimax/speech-02-hd for ragebait style.
"""

import os
import requests
from pathlib import Path
from typing import Optional

# Clean FAL_KEY environment variable BEFORE importing fal_client
# (fal_client reads it directly from env)
if os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = os.getenv("FAL_KEY", "").strip()

import fal_client
from backend.config import settings
from backend.models.schemas import CommentarySegment, LensType


class TTSClient:
    """Client for fal.ai Text-to-Speech API (ragebait style)."""
    
    def __init__(self):
        self.fal_key = os.getenv("FAL_KEY", "").strip()  # Strip whitespace/newlines
        self._available = bool(self.fal_key)
        
        if self._available:
            print("[TTS] fal.ai TTS client initialized")
        else:
            print("[TTS] Warning: FAL_KEY not set. TTS features disabled.")
    
    async def synthesize_commentary(
        self,
        segments: list[CommentarySegment],
        lens: LensType,
        output_path: Optional[str] = None
    ) -> str:
        """
        Synthesize full commentary to audio file using fal.ai.
        
        Uses ragebait style: angry emotion, fast speed (1.2x) for TikTok feel.
        
        Args:
            segments: List of commentary segments
            lens: Lens type (used for voice selection)
            output_path: Output file path (optional)
            
        Returns:
            Path to output MP3 file
        """
        if not self._available:
            raise RuntimeError("TTS client not initialized - FAL_KEY not set")
        
        if output_path is None:
            output_path = str(settings.TEMP_DIR / "commentary.mp3")
        
        # Combine all segments into one text
        full_text = self._build_full_script(segments)
        
        # Get voice settings based on lens
        voice_settings = self._get_voice_settings(lens)
        
        print(f"[TTS] Synthesizing {len(segments)} segments with fal.ai (ragebait style)")
        print(f"[TTS] Voice: {voice_settings['voice_id']}, Speed: {voice_settings['speed']}, Emotion: {voice_settings['emotion']}")
        print(f"[TTS] Text: {full_text[:100]}...")
        
        try:
            # Use fal_client.run for synchronous execution (simpler and more reliable)
            result = fal_client.run(
                "fal-ai/minimax/speech-02-hd",
                arguments={
                    "text": full_text,
                    "voice_setting": voice_settings
                }
            )
            
            if result and "audio" in result:
                audio_url = result["audio"]["url"]
                print(f"[TTS] Generated audio URL: {audio_url}")
                
                # Download the audio file
                response = requests.get(audio_url)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                print(f"[TTS] Audio saved to {output_path}")
                return output_path
            else:
                raise RuntimeError(f"fal.ai TTS failed: {result}")
                
        except Exception as e:
            print(f"[TTS] Error generating audio: {e}")
            raise
    
    def _build_full_script(self, segments: list[CommentarySegment]) -> str:
        """Build full script from segments with natural pauses."""
        parts = []
        
        for i, segment in enumerate(segments):
            # Clean text
            text = segment.text.strip()
            
            # Add the segment text
            parts.append(text)
            
            # Add pause between segments (represented by ellipsis for natural speech)
            if i < len(segments) - 1:
                parts.append("...")
        
        return " ".join(parts)
    
    def _get_voice_settings(self, lens: LensType) -> dict:
        """
        Get fal.ai voice settings optimized for ragebait content.
        
        All lenses use fast, energetic delivery for TikTok-style engagement.
        """
        # Base ragebait settings - fast and angry for maximum engagement
        base_settings = {
            "voice_id": "Wise_Woman",  # Using a different voice that works well
            "speed": 1.2,  # TikTok speed
            "vol": 1.0,
            "pitch": 0,
            "emotion": "angry"  # Ragebait style
        }
        
        # Customize slightly based on lens for variety
        lens_overrides = {
            LensType.NATURE_DOCUMENTARY: {
                "voice_id": "Wise_Woman",
                "emotion": "surprised",  # Awed at nature
                "speed": 1.1
            },
            LensType.HEIST_MOVIE: {
                "voice_id": "Wise_Woman",
                "emotion": "angry",  # Intense heist energy
                "speed": 1.3  # Extra fast for tension
            },
            LensType.ALIEN_ANTHROPOLOGIST: {
                "voice_id": "Wise_Woman",
                "emotion": "surprised",  # Confused alien
                "speed": 1.15
            },
            LensType.COOKING_SHOW: {
                "voice_id": "Wise_Woman",
                "emotion": "happy",  # Enthusiastic chef
                "speed": 1.25
            },
            LensType.SHAKESPEAREAN: {
                "voice_id": "Wise_Woman",
                "emotion": "angry",  # Dramatic theater
                "speed": 1.1
            },
            LensType.CORPORATE_MEETING: {
                "voice_id": "Wise_Woman",
                "emotion": "angry",  # Frustrated corporate drone
                "speed": 1.2
            },
            LensType.TRUE_CRIME: {
                "voice_id": "Wise_Woman",
                "emotion": "angry",  # Intense crime narrator
                "speed": 1.0  # Slower for suspense
            },
        }
        
        # Apply overrides if lens has custom settings
        if lens in lens_overrides:
            base_settings.update(lens_overrides[lens])
        
        return base_settings
    
    def is_available(self) -> bool:
        """Check if TTS client is available."""
        return self._available


# Singleton instance
tts_client = TTSClient()
