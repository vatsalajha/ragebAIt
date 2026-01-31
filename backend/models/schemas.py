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


class CommentarySegment(BaseModel):
    """A single segment of generated commentary."""
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Commentary text")
    emotion: str = Field(default="neutral", description="Emotion/tone for TTS")


class GenerateResponse(BaseModel):
    """Response from video generation endpoint."""
    video_id: str = Field(..., description="Unique ID for the generated video")
    video_url: str = Field(..., description="URL to the generated video with commentary")
    thumbnail_url: Optional[str] = Field(default=None, description="URL to video thumbnail")
    commentary_segments: list[CommentarySegment] = Field(..., description="Generated commentary segments")
    lens: LensType = Field(..., description="Lens used for generation")
    duration: float = Field(..., description="Video duration in seconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="ok")
    version: str = Field(default="1.0.0")
    services: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error info")
