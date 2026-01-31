"""
ragebAIt - Nano Banana Meme Engine
Uses Gemini's native image generation for gen-z sports memes.
Based on banana.py implementation.
"""

import os
import io
import base64
import json
import re
from typing import Optional
from PIL import Image

from google import genai
from google.genai import types

from backend.config import settings


class NanoBananaMemeEngine:
    """Generates gen-z sports memes using Gemini's native image generation (Nano Banana)."""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the Gemini client with API key."""
        try:
            api_key = settings.GEMINI_API_KEY
            
            if api_key:
                self.client = genai.Client(api_key=api_key)
                print(f"[Meme] Nano Banana initialized with API key")
            else:
                print("[Meme] Warning: GEMINI_API_KEY not set. Nano Banana disabled.")
                self.client = None
        except Exception as e:
            print(f"[Meme] Warning: Could not initialize Nano Banana: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Nano Banana is available."""
        return self.client is not None
    
    async def generate_meme(
        self,
        frame_base64: str,
        context: str = "",
        output_path: Optional[str] = None
    ) -> dict:
        """
        Generate a gen-z sports meme from a video frame.
        
        Args:
            frame_base64: Base64 encoded image frame
            context: Optional context about the video/moment
            output_path: Optional path to save the generated meme
            
        Returns:
            Dictionary with:
            - image_base64: Base64 encoded generated meme
            - caption: Social media caption with hashtags
            - image_prompt: The prompt used to generate the image
            - style: The meme style used
        """
        if not self.client:
            raise RuntimeError("Nano Banana client not initialized - GEMINI_API_KEY not set")
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(frame_base64)
        mime_type = "image/jpeg"
        
        # Step 1: Analyze the image and get meme content from Gemini
        print("[Meme] Analyzing frame for meme potential...")
        
        analysis_prompt = f"""Analyze this sports image and create gen-z meme content for it.

This is a frame from a sports video. {f'Context: {context}' if context else ''}

This is a SPORTS image - focus on the athletic context, players, teams, game moments, 
fan reactions, or sports culture shown.

Respond in this exact JSON format:
{{
    "image_prompt": "<a detailed prompt for generating/editing the image into a sports meme>",
    "caption": "<a short, punchy social media caption with relevant hashtags for Twitter/Instagram, max 280 chars>",
    "style": "<choose one: deepfried, surreal, wholesome, cursed, clean, chaotic>"
}}

STYLE OPTIONS (pick what fits the vibe best):
- "deepfried": Oversaturated colors, lens flares, emojis, warped/distorted, ironic humor. Best for absurd or ironic moments.
- "surreal": Weird edits, unexpected objects, dreamlike, makes no sense but is funny. Good for bizarre plays or reactions.
- "wholesome": Clean edit with heartwarming twist, feel-good energy. For touching sports moments.
- "cursed": Unsettling, weird cropping, ominous energy, "this image has an aura". For awkward or creepy frames.
- "clean": Professional-looking meme, clear text overlays, polished. For moments that speak for themselves.
- "chaotic": Maximum chaos, multiple elements, sensory overload, gen-z brain rot energy. For wild game moments.

Make it funny, relatable to sports fans, and capture that chaotic gen-z meme energy.
Use sports references, player/team jokes, and current meme formats.
Only respond with the JSON, nothing else."""

        analysis_response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        types.Part.from_text(text=analysis_prompt)
                    ]
                )
            ]
        )
        
        # Parse the JSON response
        try:
            response_text = analysis_response.text.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                response_text = json_match.group(1).strip()
            meme_content = json.loads(response_text)
        except json.JSONDecodeError:
            meme_content = {
                "image_prompt": analysis_response.text.strip(),
                "caption": "🔥 Sports moment hits different #sports #meme",
                "style": "chaotic"
            }
        
        print(f"[Meme] Generated prompt: {meme_content['image_prompt'][:100]}...")
        print(f"[Meme] Caption: {meme_content['caption']}")
        print(f"[Meme] Style: {meme_content.get('style', 'clean')}")
        
        # Step 2: Use Nano Banana (Gemini 3 Pro Image) to generate/edit the image
        style = meme_content.get('style', 'clean')
        
        style_instructions = {
            "deepfried": "Deep fry this image with oversaturated colors, add lens flares, random emojis (😂🔥💀), slight warping/distortion, and crusty JPEG artifacts.",
            "surreal": "Make this surreal and dreamlike - add unexpected objects, weird perspective shifts, or absurd elements that don't belong.",
            "wholesome": "Keep this clean and heartwarming - subtle edits that enhance the feel-good moment.",
            "cursed": "Make this cursed - unsettling cropping, ominous lighting, weird blur effects, 'this image has an aura' energy.",
            "clean": "Create a clean, polished meme - clear composition with any text overlays crisp and readable.",
            "chaotic": "Maximum chaos - add multiple meme elements, overlay effects, sensory overload, pure gen-z brain rot energy."
        }
        
        style_prompt = style_instructions.get(style, style_instructions["clean"])
        edit_prompt = f"{style_prompt} Transform this sports image into a gen-z meme: {meme_content['image_prompt']}"
        
        print(f"[Meme] Generating meme with Nano Banana (style: {style})...")
        
        image_response = self.client.models.generate_content(
            model="gemini-3-pro-image-preview",  # Nano Banana Pro - Gemini 3 Pro Image
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        types.Part.from_text(text=edit_prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        
        # Extract the generated image from the response
        generated_image = None
        for part in image_response.candidates[0].content.parts:
            if part.inline_data is not None:
                # The data is already bytes
                image_data = part.inline_data.data
                if isinstance(image_data, str):
                    image_data = base64.b64decode(image_data)
                generated_image = Image.open(io.BytesIO(image_data))
                break
        
        if generated_image is None:
            raise ValueError("No image was generated by Nano Banana")
        
        # Convert to base64
        output_buffer = io.BytesIO()
        generated_image.save(output_buffer, format='PNG')
        generated_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        # Save if output path provided
        if output_path:
            generated_image.save(output_path)
            print(f"[Meme] Saved to {output_path}")
        
        print(f"[Meme] ✅ Meme generated successfully!")
        
        return {
            "image_base64": generated_base64,
            "caption": meme_content['caption'],
            "image_prompt": meme_content['image_prompt'],
            "style": style
        }


# Singleton instance
meme_engine = NanoBananaMemeEngine()
