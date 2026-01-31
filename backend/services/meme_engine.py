"""
ragebAIt - Meme Generation Engine
Handles meme rendering with text overlays.
"""

import io
import base64
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from backend.config import settings

from backend.models.schemas import MemeCaption, MemeFormat


class MemeEngine:
    """Generates memes from frames with text overlays."""
    
    # Format sizes
    FORMATS = {
        MemeFormat.SQUARE: (1080, 1080),
        MemeFormat.WIDE: (1200, 675),
        MemeFormat.TALL: (1080, 1920),
    }
    
    def __init__(self):
        self.font_path = self._find_font()
    
    def _find_font(self) -> Optional[str]:
        """Find a suitable font for meme text."""
        # Common font paths
        font_candidates = [
            "/System/Library/Fonts/Supplemental/Impact.ttf",  # macOS
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",  # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux alt
            "C:\\Windows\\Fonts\\Impact.ttf",  # Windows
        ]
        
        for font_path in font_candidates:
            if Path(font_path).exists():
                return font_path
        
        return None
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font at specified size."""
        if self.font_path:
            return ImageFont.truetype(self.font_path, size)
        else:
            # Fallback to default font
            return ImageFont.load_default()
    
    def render_meme(
        self,
        frame_base64: str,
        caption: MemeCaption,
        format: MemeFormat = MemeFormat.SQUARE
    ) -> bytes:
        """
        Render a meme from frame and caption.
        
        Args:
            frame_base64: Base64 encoded image
            caption: Caption configuration
            format: Output format
            
        Returns:
            PNG image as bytes
        """
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64)
        img = Image.open(io.BytesIO(frame_bytes))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to target format
        target_size = self.FORMATS.get(format, self.FORMATS[MemeFormat.SQUARE])
        img = self._resize_and_crop(img, target_size)
        
        # Apply text based on template
        if caption.template == "classic":
            img = self._render_classic_meme(img, caption)
        elif caption.template == "modern":
            img = self._render_modern_meme(img, caption)
        elif caption.template == "quote":
            img = self._render_quote_meme(img, caption)
        else:
            img = self._render_classic_meme(img, caption)
        
        # Export
        output = io.BytesIO()
        img.save(output, format='PNG', quality=95)
        return output.getvalue()
    
    def _resize_and_crop(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """Resize and crop image to target size while maintaining aspect ratio."""
        target_ratio = target_size[0] / target_size[1]
        img_ratio = img.width / img.height
        
        if img_ratio > target_ratio:
            # Image is wider - crop sides
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            # Image is taller - crop top/bottom
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))
        
        return img.resize(target_size, Image.LANCZOS)
    
    def _render_classic_meme(self, img: Image.Image, caption: MemeCaption) -> Image.Image:
        """Render classic Impact font top/bottom meme."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Calculate font size based on image width
        font_size = int(width * 0.08)
        font = self._get_font(font_size)
        stroke_width = max(2, font_size // 15)
        
        # Draw top text
        if caption.top_text:
            text = caption.top_text.upper()
            self._draw_text_with_outline(
                draw, text, font,
                position=(width // 2, int(height * 0.08)),
                stroke_width=stroke_width
            )
        
        # Draw bottom text
        if caption.bottom_text:
            text = caption.bottom_text.upper()
            self._draw_text_with_outline(
                draw, text, font,
                position=(width // 2, int(height * 0.92)),
                stroke_width=stroke_width,
                anchor="bottom"
            )
        
        return img
    
    def _render_modern_meme(self, img: Image.Image, caption: MemeCaption) -> Image.Image:
        """Render modern meme with white caption bar."""
        width, height = img.size
        
        # Add white bar at top
        bar_height = int(height * 0.12)
        new_img = Image.new('RGB', (width, height + bar_height), 'white')
        new_img.paste(img, (0, bar_height))
        
        draw = ImageDraw.Draw(new_img)
        
        # Draw caption text in bar
        if caption.caption:
            font_size = int(bar_height * 0.5)
            font = self._get_font(font_size)
            
            # Word wrap if needed
            lines = self._wrap_text(caption.caption, font, width - 40)
            
            y = bar_height // 2 - (len(lines) * font_size) // 2
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y), line, font=font, fill='black')
                y += font_size + 5
        
        return new_img
    
    def _render_quote_meme(self, img: Image.Image, caption: MemeCaption) -> Image.Image:
        """Render quote-style meme with semi-transparent overlay."""
        width, height = img.size
        
        # Create semi-transparent overlay at bottom
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Draw gradient overlay at bottom
        overlay_height = int(height * 0.3)
        for i in range(overlay_height):
            alpha = int(180 * (i / overlay_height))
            overlay_draw.line(
                [(0, height - overlay_height + i), (width, height - overlay_height + i)],
                fill=(0, 0, 0, alpha)
            )
        
        # Convert img to RGBA and composite
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        # Draw quote text
        draw = ImageDraw.Draw(img)
        
        text = caption.caption or caption.bottom_text or ""
        if text:
            font_size = int(width * 0.05)
            font = self._get_font(font_size)
            
            lines = self._wrap_text(text, font, width - 60)
            
            y = height - int(overlay_height * 0.8)
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y), line, font=font, fill='white')
                y += font_size + 5
        
        return img.convert('RGB')
    
    def _draw_text_with_outline(
        self,
        draw: ImageDraw.Draw,
        text: str,
        font: ImageFont.FreeTypeFont,
        position: tuple,
        stroke_width: int = 3,
        text_color: str = 'white',
        stroke_color: str = 'black',
        anchor: str = "top"
    ):
        """Draw text with stroke outline (classic meme style)."""
        x, y = position
        
        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center horizontally
        x = x - text_width // 2
        
        # Adjust vertical position
        if anchor == "bottom":
            y = y - text_height
        
        # Draw stroke (outline)
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            
            # Use a dummy draw to measure
            dummy_img = Image.new('RGB', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
            
            if bbox[2] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


# Singleton instance
meme_engine = MemeEngine()
