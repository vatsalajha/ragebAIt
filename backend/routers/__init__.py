"""
ragebAIt - API Routers
"""

from .generate import router as generate_router
from .meme import router as meme_router
from .parody import router as parody_router

__all__ = ["generate_router", "meme_router", "parody_router"]
