import aiohttp
import os
import base64
import logging

logger = logging.getLogger(__name__)

async def download_video(encoded_url: str, ucrid: str) -> str:
    """
    Downloads a video from a Base64-encoded URL.
    """
    try:
        media_url = base64.b64decode(encoded_url).decode('utf-8')
        filename = f"{ucrid}.mp4"
        directory = "app/resources"
        video_path = os.path.join(directory, filename)
        
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(media_url) as response:
                response.raise_for_status()
                with open(video_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
        
        logger.info(f"Downloaded video to {video_path}")
        return filename
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        raise RuntimeError(f"Failed to download video: {e}")
