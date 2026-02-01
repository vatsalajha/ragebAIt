"""
ragebAIt - Gemini API Client
Handles video analysis, funny moment detection, and comedy commentary generation.
"""

import json
import time
import re
from typing import Optional
from dataclasses import dataclass

import google.generativeai as genai
from backend.config import settings
from backend.models.schemas import CommentarySegment, LensType

from backend.prompts.lenses import get_lens_prompt, get_lens_config


@dataclass
class FunnyMoment:
    """A detected funny/interesting moment in the video."""
    start_time: float
    end_time: float
    description: str
    humor_score: int  # 1-10
    reason: str


class GeminiClient:
    """Client for interacting with Gemini 2.0 Flash API."""
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": 0.9,  # Higher for creativity
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
    
    async def analyze_video(
        self,
        video_path: str,
        lens: LensType,
        context: Optional[dict] = None,
        video_duration: float = 30.0
    ) -> list[CommentarySegment]:
        """
        Analyze video and generate comedic commentary.
        
        Args:
            video_path: Path to video file
            lens: Comedy lens to apply
            context: Optional context from Browser Use (team info, player stats)
            video_duration: Duration of video in seconds
            
        Returns:
            List of CommentarySegment objects
        """
        # Upload video to Gemini
        print(f"[Gemini] Uploading video: {video_path}")
        video_file = genai.upload_file(video_path)
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            print("[Gemini] Processing video...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            raise Exception(f"Video processing failed: {video_file.state.name}")
        
        print(f"[Gemini] Video ready: {video_file.uri}")
        
        # Build prompt
        prompt = self._build_commentary_prompt(lens, context, video_duration)
        
        # Generate commentary
        print(f"[Gemini] Generating {lens.value} commentary...")
        response = self.model.generate_content(
            [video_file, prompt],
            request_options={"timeout": 120}
        )
        
        # Clean up uploaded file
        try:
            genai.delete_file(video_file.name)
        except Exception:
            pass  # Ignore cleanup errors
        
        # Parse response
        response_text = self._get_response_text(response)
        segments = self._parse_commentary_response(response_text)
        
        print(f"[Gemini] Generated {len(segments)} commentary segments")
        return segments
    
    async def find_funny_moments(
        self,
        video_path: str,
        video_duration: float = 0,
        min_clip_duration: float = 8.0,
        max_clip_duration: float = 30.0,
        num_moments: int = 3
    ) -> list[FunnyMoment]:
        """
        Analyze a longer video to find complete funny/interesting scenes.
        
        Args:
            video_path: Path to video file
            min_clip_duration: Minimum clip length in seconds
            max_clip_duration: Maximum clip length in seconds
            num_moments: Number of moments to find
            
        Returns:
            List of FunnyMoment objects, sorted by humor_score (highest first)
        """
        # Upload video to Gemini
        print(f"[Gemini] Uploading video for scene detection: {video_path}")
        video_file = genai.upload_file(video_path)
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            print("[Gemini] Processing video...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            raise Exception(f"Video processing failed: {video_file.state.name}")
        
        print(f"[Gemini] Video ready: {video_file.uri}")
        
        # Build prompt for finding complete scenes
        prompt = f"""
You are an expert at finding viral, funny, and engaging COMPLETE SCENES in videos for short-form content (TikTok, Reels, Shorts).

Watch this video carefully and identify the TOP {num_moments} COMPLETE SCENES that would make the BEST clips for ragebait/viral content.

VIDEO DURATION: {video_duration:.1f} seconds.
DO NOT suggest timestamps outside [0, {video_duration:.1f}].

CRITICAL: IDENTIFY COMPLETE SCENES - NOT ARBITRARY CUTS!
- A scene starts when the action/play BEGINS
- A scene ends when the action/play COMPLETES (goal scored, play finished, reaction complete, etc.)
- NEVER cut in the middle of an action - wait for it to finish!
- Include the full build-up AND the payoff/result

WHAT MAKES A GOOD SCENE:
- Fails, mistakes, or embarrassing moments WITH the aftermath/reaction
- Complete plays from start to finish
- A moment building up to a climax/payoff
- Full reactions (not cut off mid-expression)
- The setup AND the punchline

SCENE BOUNDARY RULES:
- START: When the relevant action begins (player receives ball, approach starts, etc.)
- END: When the action is FULLY COMPLETE (celebration ends, players reset, camera cuts away)
- Minimum duration: {min_clip_duration} seconds
- Maximum duration: {max_clip_duration} seconds
- If a scene is longer than {max_clip_duration}s, find a natural break point

Return ONLY valid JSON array with exactly {num_moments} complete scenes:
[
  {{
    "start_time": <float - when the scene/action BEGINS>,
    "end_time": <float - when the scene/action is FULLY COMPLETE>,
    "description": "<what happens from start to finish>",
    "humor_score": <1-10, where 10 is viral-worthy>,
    "reason": "<why this complete scene would go viral>"
  }}
]

Sort by humor_score descending (best scene first).
IMPORTANT: Make sure end_time captures the COMPLETE scene - don't cut off early!
"""
        
        print(f"[Gemini] Finding funny moments...")
        response = self.model.generate_content(
            [video_file, prompt],
            request_options={"timeout": 120}
        )
        
        # Clean up uploaded file
        try:
            genai.delete_file(video_file.name)
        except Exception:
            pass
        
        # Parse response
        response_text = self._get_response_text(response)
        moments_data = self._parse_json_response(response_text, [])
        
        moments = []
        for item in moments_data:
            try:
                moment = FunnyMoment(
                    start_time=float(item.get("start_time", 0)),
                    end_time=float(item.get("end_time", 15)),
                    description=str(item.get("description", "")),
                    humor_score=int(item.get("humor_score", 5)),
                    reason=str(item.get("reason", ""))
                )
                
                # Only enforce minimum - let scenes complete naturally
                duration = moment.end_time - moment.start_time
                if duration < min_clip_duration:
                    # Extend to minimum if too short
                    moment.end_time = moment.start_time + min_clip_duration
                
                # FINAL SAFETY: Ensure times are within video bounds
                if video_duration > 0:
                    if moment.start_time >= video_duration:
                        moment.start_time = max(0, video_duration - min_clip_duration)
                    if moment.end_time > video_duration:
                        moment.end_time = video_duration
                
                if moment.start_time >= moment.end_time:
                    moment.end_time = moment.start_time + min_clip_duration
                
                moments.append(moment)
            except (ValueError, KeyError) as e:
                print(f"[Gemini] Warning: Failed to parse moment: {e}")
                continue
        
        # Sort by humor score (highest first)
        moments.sort(key=lambda m: m.humor_score, reverse=True)
        
        print(f"[Gemini] Found {len(moments)} funny moments")
        for i, m in enumerate(moments):
            print(f"  {i+1}. [{m.start_time:.1f}s-{m.end_time:.1f}s] Score: {m.humor_score}/10 - {m.description[:50]}...")
        
        return moments
    
    async def generate_ragebait_commentary(
        self,
        video_path: str,
        moment: FunnyMoment,
        lens: LensType,
        context: Optional[dict] = None
    ) -> list[CommentarySegment]:
        """
        Generate ragebait-style commentary for a specific funny moment clip.
        
        This generates SHORT, PUNCHY, FAST commentary designed for viral short-form content.
        
        Args:
            video_path: Path to the EXTRACTED clip (not the full video)
            moment: The funny moment info for context
            lens: Comedy lens to apply
            context: Optional additional context
            
        Returns:
            List of CommentarySegment objects
        """
        # Upload video clip to Gemini
        print(f"[Gemini] Uploading clip for ragebait commentary: {video_path}")
        video_file = genai.upload_file(video_path)
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            print("[Gemini] Processing clip...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            raise Exception(f"Clip processing failed: {video_file.state.name}")
        
        # Get clip duration
        clip_duration = moment.end_time - moment.start_time
        
        # Build ragebait-optimized prompt
        prompt = self._build_ragebait_prompt(lens, moment, clip_duration, context)
        
        print(f"[Gemini] Generating ragebait {lens.value} commentary...")
        response = self.model.generate_content(
            [video_file, prompt],
            request_options={"timeout": 120}
        )
        
        # Clean up
        try:
            genai.delete_file(video_file.name)
        except Exception:
            pass
        
        response_text = self._get_response_text(response)
        segments = self._parse_commentary_response(response_text)
        
        print(f"[Gemini] Generated {len(segments)} ragebait commentary segments")
        return segments
    
    def _build_ragebait_prompt(
        self,
        lens: LensType,
        moment: FunnyMoment,
        clip_duration: float,
        context: Optional[dict]
    ) -> str:
        """Build prompt optimized for ragebait/viral short-form content."""
        
        base_prompt = get_lens_prompt(lens.value)
        
        ragebait_instructions = f"""
RAGEBAIT MODE ACTIVATED! 🔥

This is a {clip_duration:.0f}-second clip extracted from a longer video.

WHAT HAPPENS IN THIS CLIP:
{moment.description}

WHY THIS MOMENT IS VIRAL-WORTHY:
{moment.reason}

RAGEBAIT COMMENTARY RULES:
1. Be LOUD, FAST, and ENERGETIC - this is TikTok content!
2. Use short, punchy sentences (2-5 seconds each max)
3. React like you're SHOCKED, ANGRY, or HYPED
4. Use phrases like:
   - "BRO WAIT-"
   - "NO WAY HE JUST-"
   - "ARE YOU KIDDING ME?!"
   - "THIS IS INSANE!"
   - "LOOK AT THIS!"
   - "HOW IS THAT EVEN-"
5. Build to the key moment - tease it, react to it, emphasize it
6. Make viewers want to COMMENT and SHARE
7. End with something that makes viewers want to rewatch

CLIP DURATION: {clip_duration:.1f} seconds
Generate 2-4 short, punchy commentary segments that cover the clip.
Each segment should be 2-5 seconds when spoken FAST (1.2x speed).

OUTPUT FORMAT - Return ONLY valid JSON array:
[
  {{
    "start_time": 0.0,
    "end_time": <float>,
    "text": "SHORT PUNCHY RAGEBAIT TEXT",
    "emotion": "excited|tense|dramatic"
  }}
]
"""
        
        if context:
            context_section = "\n\nCONTEXT TO REFERENCE:"
            if "teams" in context:
                context_section += f"\n- Teams: {context['teams']}"
            if "players" in context:
                context_section += f"\n- Players: {context['players']}"
            ragebait_instructions += context_section
        
        return base_prompt + "\n\n" + ragebait_instructions
    
    async def analyze_frames(
        self,
        frames: list[dict],
        lens: LensType,
        context: Optional[dict] = None,
        video_duration: float = 30.0
    ) -> list[CommentarySegment]:
        """
        Analyze video frames and generate commentary (fallback if video upload fails).
        
        Args:
            frames: List of dicts with 'timestamp' and 'image_base64'
            lens: Comedy lens to apply
            context: Optional context
            video_duration: Total video duration
            
        Returns:
            List of CommentarySegment objects
        """
        # Build prompt
        prompt = self._build_commentary_prompt(lens, context, video_duration)
        
        # Prepare content parts
        content_parts = [prompt, "\n\nVideo frames in sequence:\n"]
        
        for i, frame in enumerate(frames):
            content_parts.append(f"\n[Frame at {frame['timestamp']}s]:")
            # Create image part from base64
            content_parts.append({
                "mime_type": "image/jpeg",
                "data": frame["image_base64"]
            })
        
        print(f"[Gemini] Analyzing {len(frames)} frames with {lens.value} lens...")
        response = self.model.generate_content(
            content_parts,
            request_options={"timeout": 120}
        )
        
        response_text = self._get_response_text(response)
        return self._parse_commentary_response(response_text)
    
    async def select_best_frame_for_meme(
        self,
        frames: list[dict],
        commentary_text: str
    ) -> dict:
        """
        Select the best frame for meme creation.
        
        Args:
            frames: List of dicts with 'timestamp' and 'image_base64'
            commentary_text: The generated commentary for context
            
        Returns:
            Dict with 'frame_index', 'timestamp', 'reason'
        """
        prompt = """
Analyze these video frames and select the ONE frame that would make the funniest meme.

Look for:
- Awkward poses or expressions
- Peak action moments
- Faces showing strong emotion
- Unintentionally funny compositions
- Moments that can be taken out of context

Commentary context:
""" + commentary_text + """

Return ONLY valid JSON:
{
    "best_frame_index": <number>,
    "timestamp": <float>,
    "reason": "<why this frame is meme-worthy>"
}
"""
        
        content_parts = [prompt, "\n\nFrames:\n"]
        
        for i, frame in enumerate(frames):
            content_parts.append(f"\n[Frame {i} at {frame['timestamp']}s]:")
            content_parts.append({
                "mime_type": "image/jpeg",
                "data": frame["image_base64"]
            })
        
        response = self.model.generate_content(content_parts)
        
        response_text = self._get_response_text(response)
        return self._parse_json_response(response_text, {
            "best_frame_index": 0,
            "timestamp": 0.0,
            "reason": "First frame selected as default"
        })
    
    async def generate_meme_captions(
        self,
        frame_base64: str,
        commentary_text: str,
        lens: LensType
    ) -> list[dict]:
        """
        Generate meme caption options for a frame.
        
        Args:
            frame_base64: Base64 encoded frame image
            commentary_text: Generated commentary for context
            lens: The lens used (for style matching)
            
        Returns:
            List of caption dicts
        """
        lens_config = get_lens_config(lens.value)
        meme_examples = ""
        if lens_config:
            meme_examples = "\nExamples for this style:\n" + "\n".join(
                f"- {t}" for t in lens_config.meme_templates[:2]
            )
        
        prompt = f"""
Create 3 different meme captions for this sports frame.

STYLE: {lens.value} - Match this comedic style!
{meme_examples}

COMMENTARY CONTEXT:
{commentary_text}

Generate captions that are:
1. Short and punchy (max 10 words per line)
2. Internet meme format (relatable, shareable)
3. FUNNY - make people want to share it!

Return ONLY valid JSON array:
[
    {{
        "id": "caption_1",
        "top_text": "TOP LINE" or null,
        "bottom_text": "BOTTOM LINE" or null,
        "caption": "Modern caption style" or null,
        "template": "classic|modern|quote",
        "humor_rating": 1-10
    }},
    ...
]
"""
        
        response = self.model.generate_content([
            {"mime_type": "image/jpeg", "data": frame_base64},
            prompt
        ])
        
        response_text = self._get_response_text(response)
        captions = self._parse_json_response(response_text, [])
        
        if not captions:
            # Fallback captions
            captions = [
                {
                    "id": "caption_1",
                    "top_text": "WHEN YOU",
                    "bottom_text": "SEE IT",
                    "template": "classic",
                    "humor_rating": 7
                },
                {
                    "id": "caption_2",
                    "caption": "Nobody: ... | This guy:",
                    "template": "modern",
                    "humor_rating": 6
                },
                {
                    "id": "caption_3",
                    "top_text": "THAT MOMENT",
                    "bottom_text": "YOU KNEW",
                    "template": "classic",
                    "humor_rating": 7
                }
            ]
        
        return captions
    
    def _get_response_text(self, response) -> str:
        """Safely extract text from Gemini response."""
        try:
            return response.text
        except Exception:
            try:
                # Fallback: try to get text from candidates
                return response.candidates[0].content.parts[0].text
            except Exception as e:
                print(f"[Gemini] Warning: Could not extract response text: {e}")
                return ""
    
    def _build_commentary_prompt(
        self,
        lens: LensType,
        context: Optional[dict],
        video_duration: float
    ) -> str:
        """Build the full prompt for commentary generation."""
        
        prompt_parts = [get_lens_prompt(lens.value)]
        
        prompt_parts.append(f"\nVIDEO DURATION: {video_duration:.1f} seconds")
        prompt_parts.append("Generate commentary segments covering the full duration.")
        
        # Add context if provided (from Browser Use)
        if context:
            context_section = "\n\nREAL-WORLD CONTEXT (use to make jokes more specific):"
            if "teams" in context:
                context_section += f"\n- Teams: {context['teams']}"
            if "players" in context:
                context_section += f"\n- Key Players: {context['players']}"
            if "recent_news" in context:
                context_section += f"\n- Recent News: {context['recent_news']}"
            if "score" in context:
                context_section += f"\n- Score: {context['score']}"
            prompt_parts.append(context_section)
        
        prompt_parts.append("\n\nNow watch the video and generate your hilarious miscommentary!")
        
        return "\n".join(prompt_parts)
    
    def _parse_commentary_response(self, response_text: str) -> list[CommentarySegment]:
        """Parse Gemini's response into CommentarySegment objects."""
        
        # Try to extract JSON from response
        json_data = self._parse_json_response(response_text, [])
        
        segments = []
        for item in json_data:
            try:
                segments.append(CommentarySegment(
                    start_time=float(item.get("start_time", 0)),
                    end_time=float(item.get("end_time", 5)),
                    text=str(item.get("text", "")),
                    emotion=str(item.get("emotion", "neutral"))
                ))
            except (ValueError, KeyError) as e:
                print(f"[Gemini] Warning: Failed to parse segment: {e}")
                continue
        
        # Fallback if no segments parsed
        if not segments:
            segments = [CommentarySegment(
                start_time=0,
                end_time=10,
                text="And here we see... something happening. Truly remarkable.",
                emotion="confused"
            )]
        
        return segments
    
    def _parse_json_response(self, response_text: str, default):
        """Extract JSON from response text."""
        
        # Try to find JSON in response
        json_str = response_text.strip()
        
        # Remove markdown code blocks if present
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        
        # Try to find JSON array or object
        json_match = re.search(r'[\[\{].*[\]\}]', json_str, re.DOTALL)
        if json_match:
            json_str = json_match.group()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"[Gemini] Warning: Failed to parse JSON: {e}")
            print(f"[Gemini] Raw response: {response_text[:500]}...")
            return default


# Singleton instance
gemini_client = GeminiClient()
