"""
ragebAIt - Configuration Management
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env first, then fallback to CWD .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys (strip whitespace to avoid header issues)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    FAL_KEY: str = os.getenv("FAL_KEY", "").strip()  # fal.ai TTS API key
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    VERCEL_BLOB_TOKEN: str = os.getenv("VERCEL_BLOB_TOKEN", "").strip()
    
    # App Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"
    
    # File Settings
    MAX_VIDEO_SIZE_MB: int = 50
    MAX_VIDEO_DURATION_SECONDS: int = 120
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".mov", ".avi", ".webm"}
    
    # Temp directory for processing
    TEMP_DIR: Path = Path("/tmp/ragebait")
    
    # Gemini Model
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    
    def __init__(self):
        # Create temp directory if it doesn't exist
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> list[str]:
        """Validate required settings. Returns list of missing configs."""
        errors = []
        
        if not self.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required")
        
        if not self.VERCEL_BLOB_TOKEN and not self.MOCK_MODE:
            errors.append("VERCEL_BLOB_TOKEN is required (or enable MOCK_MODE)")
        
        return errors


# Global settings instance
settings = Settings()
