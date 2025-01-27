import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def cleanup_media_files(filename: str) -> None:
    """
    Removes downloaded media files and their derivatives after processing
    Args:
        filename: The base filename of the media file
    """
    try:
        base_path = Path("app/resources")
        base_name = Path(filename).stem
        
        # List of possible extensions to clean up
        extensions = ['.mp4', '.wav', '.jpg', '.png']
        
        for ext in extensions:
            file_path = base_path / f"{base_name}{ext}"
            if file_path.exists():
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
                
    except Exception as e:
        logger.error(f"Error cleaning up files for {filename}: {e}") 