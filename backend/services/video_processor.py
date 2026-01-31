"""
ragebAIt - Video Processing Service
Handles frame extraction, video/audio merging, clip extraction, and video manipulation.
"""

import cv2
import base64
import tempfile
from pathlib import Path
from typing import Optional
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

from backend.config import settings


class VideoProcessor:
    """Handles video processing operations."""
    
    def __init__(self):
        self.temp_dir = settings.TEMP_DIR
    
    def extract_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extract a clip from a video between start_time and end_time.
        
        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Optional output path (generates temp file if not provided)
            
        Returns:
            Path to extracted clip
        """
        if output_path is None:
            output_path = str(self.temp_dir / f"clip_{start_time:.0f}_{end_time:.0f}.mp4")
        
        print(f"[Video] Extracting clip: {start_time:.1f}s - {end_time:.1f}s")
        
        # Load video
        video = VideoFileClip(video_path)
        
        # Ensure times are within bounds
        start_time = max(0, start_time)
        end_time = min(video.duration, end_time)
        
        # Extract subclip
        clip = video.subclip(start_time, end_time)
        
        # Write clip
        clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(self.temp_dir / 'temp_clip_audio.m4a'),
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Cleanup
        clip.close()
        video.close()
        
        print(f"[Video] Clip saved to {output_path}")
        return output_path
    
    def extract_frames(
        self, 
        video_path: str, 
        fps: float = 1.0,
        max_frames: int = 30
    ) -> list[dict]:
        """
        Extract frames from video at specified FPS.
        
        Args:
            video_path: Path to video file
            fps: Frames per second to extract (default 1)
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of dicts with 'timestamp' and 'image_base64' keys
        """
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / video_fps if video_fps > 0 else 0
        
        # Calculate frame interval
        frame_interval = int(video_fps / fps) if fps > 0 else int(video_fps)
        
        frame_count = 0
        extracted_count = 0
        
        while cap.isOpened() and extracted_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Encode to JPEG
                _, buffer = cv2.imencode('.jpg', frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, 85])
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                timestamp = frame_count / video_fps
                
                frames.append({
                    'timestamp': round(timestamp, 2),
                    'image_base64': image_base64,
                    'frame_index': frame_count
                })
                extracted_count += 1
            
            frame_count += 1
        
        cap.release()
        return frames
    
    def extract_frame_at_timestamp(
        self, 
        video_path: str, 
        timestamp: float
    ) -> Optional[str]:
        """
        Extract a single frame at a specific timestamp.
        
        Args:
            video_path: Path to video file
            timestamp: Time in seconds
            
        Returns:
            Base64 encoded JPEG image
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp * video_fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        return base64.b64encode(buffer).decode('utf-8')
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata.
        
        Returns:
            Dict with 'duration', 'fps', 'width', 'height', 'total_frames'
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'duration': round(duration, 2),
            'fps': fps,
            'width': width,
            'height': height,
            'total_frames': total_frames
        }
    
    def merge_audio_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: Optional[str] = None,
        keep_original_audio: bool = True,
        original_audio_volume: float = 0.2
    ) -> str:
        """
        Merge audio with video file.
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file (MP3 or WAV)
            output_path: Output path (optional, generates temp file if not provided)
            keep_original_audio: Whether to keep original video audio
            original_audio_volume: Volume of original audio (0-1)
            
        Returns:
            Path to output video file
        """
        if output_path is None:
            output_path = str(self.temp_dir / f"merged_{Path(video_path).stem}.mp4")
        
        # Load video
        video_clip = VideoFileClip(video_path)
        
        # Load new audio
        new_audio = AudioFileClip(audio_path)
        
        # Trim audio to video length if needed
        if new_audio.duration > video_clip.duration:
            new_audio = new_audio.subclip(0, video_clip.duration)
        
        if keep_original_audio and video_clip.audio is not None:
            # Mix original audio (lowered) with new commentary
            original_audio = video_clip.audio.volumex(original_audio_volume)
            final_audio = CompositeAudioClip([original_audio, new_audio])
        else:
            final_audio = new_audio
        
        # Set audio to video
        final_video = video_clip.set_audio(final_audio)
        
        # Write output
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(self.temp_dir / 'temp_audio.m4a'),
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Cleanup
        video_clip.close()
        new_audio.close()
        
        return output_path
    
    def create_thumbnail(
        self,
        video_path: str,
        timestamp: Optional[float] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a thumbnail from video.
        
        Args:
            video_path: Path to video
            timestamp: Time to capture (default: 25% into video)
            output_path: Output path for thumbnail
            
        Returns:
            Path to thumbnail image
        """
        if output_path is None:
            output_path = str(self.temp_dir / f"thumb_{Path(video_path).stem}.jpg")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Default to 25% into video
        if timestamp is None:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            timestamp = duration * 0.25
        
        frame_base64 = self.extract_frame_at_timestamp(video_path, timestamp)
        
        if frame_base64:
            # Decode and save
            img_data = base64.b64decode(frame_base64)
            with open(output_path, 'wb') as f:
                f.write(img_data)
        
        cap.release()
        return output_path


# Singleton instance
video_processor = VideoProcessor()
