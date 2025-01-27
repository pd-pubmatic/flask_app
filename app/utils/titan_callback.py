import aiohttp
import logging
from config import Config

logger = logging.getLogger(__name__)

async def callback_tag_results(payload: dict, callback_url: str):
    """Send results to callback URL with retry logic."""
    timeout = aiohttp.ClientTimeout(total=Config.CALLBACK_TIMEOUT)
    
    for attempt in range(Config.CALLBACK_RETRIES):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(callback_url, json=payload) as response:
                    response.raise_for_status()
                    logger.info(f"Successfully sent callback to {callback_url}")
                    return
        except Exception as e:
            logger.error(f"Callback attempt {attempt + 1} failed: {e}")
            if attempt == Config.CALLBACK_RETRIES - 1:
                #send error notification to slack
                pass