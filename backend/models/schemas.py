"""
ragebAIt - Pydantic Schemas for API Request/Response
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LensType(str, Enum):
    """Available comedy lens types."""
    NATURE_DOCUMENTARY = "nature_documentary"
    HEIST_MOVIE = "heist_movie"
    ALIEN_ANTHROPOLOGIST = "alien_anthropologist"
    COOKING_SHOW = "cooking_show"
    SHAKESPEAREAN = "shakespearean"
    CORPORATE_MEETING = "corporate_meeting"
    TRUE_CRIME = "true_crime"


class MemeFormat(str, Enum):
    """Meme output formats."""
    SQUARE = "square"      # 1080x1080 - Instagram
    WIDE = "wide"          # 1200x675 - Twitter
    TALL = "tall"          # 1080x1920 - Stories


class CommentarySegment(BaseModel):
    """A single segment of generated commentary."""
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Commentary text")
    emotion: str = Field(default="neutral", description="Emotion/tone for TTS")


class GenerateRequest(BaseModel):
    """Request body for video generation (used with form data)."""
    lens: LensType = Field(..., description="Comedy lens to apply")
    context: Optional[dict] = Field(default=None, description="Additional context from Browser Use")


class GenerateResponse(BaseModel):
    """Response from video generation endpoint."""
    video_id: str = Field(..., description="Unique ID for the generated video")
    video_url: str = Field(..., description="URL to the generated video with commentary")
    thumbnail_url: Optional[str] = Field(default=None, description="URL to video thumbnail")
    commentary_segments: list[CommentarySegment] = Field(..., description="Generated commentary segments")
    lens: LensType = Field(..., description="Lens used for generation")
    duration: float = Field(..., description="Video duration in seconds")


class MemeCaption(BaseModel):
    """A caption option for meme generation."""
    id: str = Field(..., description="Unique caption ID")
    top_text: Optional[str] = Field(default=None, description="Top text (classic meme)")
    bottom_text: Optional[str] = Field(default=None, description="Bottom text (classic meme)")
    caption: Optional[str] = Field(default=None, description="Caption (modern meme)")
    template: str = Field(default="classic", description="Meme template style")
    humor_rating: int = Field(default=7, ge=1, le=10, description="AI-rated humor potential")


class MemeOptionsResponse(BaseModel):
    """Response with meme generation options."""
    video_id: str = Field(..., description="Video ID")
    frame_base64: str = Field(..., description="Best frame as base64 image")
    frame_timestamp: float = Field(..., description="Timestamp of selected frame")
    frame_reason: str = Field(..., description="Why this frame was selected")
    captions: list[MemeCaption] = Field(..., description="Caption options")
    lens: LensType = Field(..., description="Lens for styling")


class MemeGenerateRequest(BaseModel):
    """Request to generate final meme."""
    video_id: str = Field(..., description="Video ID to get frame from")
    caption: MemeCaption = Field(..., description="Selected caption")
    format: MemeFormat = Field(default=MemeFormat.SQUARE, description="Output format")
    use_nano_banana: bool = Field(default=True, description="Use Nano Banana for generation")


class MemeGenerateResponse(BaseModel):
    """Response with generated meme."""
    meme_id: str = Field(..., description="Unique meme ID")
    meme_url: str = Field(..., description="URL to generated meme image")
    format: MemeFormat = Field(..., description="Meme format")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="ok")
    version: str = Field(default="1.0.0")
    services: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error info")
