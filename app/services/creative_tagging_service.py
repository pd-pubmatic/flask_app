import logging
from typing import Dict, List
from app.models.creative_tag import ProcessingResult
from app.utils import titan_callback as callback_handler
from app.processors import audio_transcription, prompt_processing, video_file_download, video_ocr
import time
from app.utils.file_cleanup import cleanup_media_files
import csv
from app.utils.s3_handler import S3Handler
from config import Config
import asyncio

logger = logging.getLogger(__name__)

def load_tag_map():
    tag_map = {}
    try:
        with open(Config.TAG_MAPPING_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tag_map[row['name'].lower()] = int(row['id'])
    except Exception as e:
        logger.error(f"Error loading tag mapping: {e}")
        return {}
    return tag_map

TAG_MAP = load_tag_map()

class CreativeTaggingService:
    def __init__(self):
        self.tag_map = self._load_tag_map()
        self.s3_client = S3Handler()

    def _load_tag_map(self):
        tag_map = {}
        try:
            with open(Config.TAG_MAPPING_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tag_map[row['name'].lower()] = int(row['id'])
        except Exception as e:
            logger.error(f"Error loading tag mapping: {e}")
            return {}
        return tag_map

    async def process_batch(self, creatives: List[Dict], callback_url: str, request_id: str):
        """Process a batch of creatives in parallel with proper error handling"""
        # Create tasks for all creatives
        tasks = [self._process_single(creative) for creative in creatives]
        
        # Process all tasks in parallel
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert results list to dictionary
        results = {}
        for result in results_list:
            if isinstance(result, Exception):
                # Handle any unhandled exceptions
                logger.error(f"Unhandled exception in parallel processing: {str(result)}")
                continue
            results[result.ucrid] = result
                
        await self._handle_results(results, callback_url, request_id)

    async def _process_single(self, creative: Dict) -> ProcessingResult:
        """Process a single creative with proper error handling"""
        filename = None
        start_time = time.time()
        try:
            ucrid = creative.get('ucrid')
            media_url = creative.get('media_url')
            if not ucrid or not media_url:
                raise ValueError("Missing required 'ucrid' or 'media_url' in creative.")

            # Step 1: Download video with retry
            for attempt in range(3):
                try:
                    filename = await video_file_download.download_video(media_url, ucrid)
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2 ** attempt)

            logger.info(f"Downloaded video for UCRID {ucrid}: {filename}")

            # Step 2: Process with retries and proper error handling
            transcription = await self._process_with_retry(
                lambda: audio_transcription.transcribe_audio(filename)
            )
            
            ocr_results = await self._process_with_retry(
                lambda: video_ocr.capture_crop_frames_and_get_ocr(filename)
            )
            top_frame_ocr_list, bottom_frame_ocr_list = ocr_results

            tags = await self._process_with_retry(
                lambda: prompt_processing.getTagsForUnprocessedContent(
                    transcription, top_frame_ocr_list, bottom_frame_ocr_list
                )
            )

            processing_time = time.time() - start_time
            return ProcessingResult(
                ucrid=ucrid,
                status='success',
                tags=tags,
                processing_time=processing_time
            )
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing media for UCRID {creative.get('ucrid', 'unknown')}: {e}")
            return ProcessingResult(
                ucrid=creative.get('ucrid', 'unknown'),
                status='failed',
                error=str(e),
                processing_time=processing_time
            )
        finally:
            if filename:
                cleanup_media_files(filename)

    async def _process_with_retry(self, func, max_retries=3):
        """Generic retry mechanism for processing steps"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def _handle_results(self, results: Dict, callback_url: str, request_id: str):
        """Handle results with proper error handling"""
        tag_result = []
        for ucrid, result in results.items():
            if result.status == 'success':
                creative_tags = []
                for tag in result.tags:
                    tag_name = tag if isinstance(tag, str) else tag.get('name', '')
                    tag_name_lower = tag_name.lower()
                    
                    creative_tags.append({
                        "id": self.tag_map.get(tag_name_lower),
                        "name": tag_name,
                        "mapped": tag_name_lower in self.tag_map
                    })

                tag_result.append({
                    "ucrid": ucrid,
                    "creativeTags": creative_tags
                })

        #If tag_result is empty, print error

        if tag_result:
            payload = {
                "metadata": {
                    "request_id": request_id,
                    "status": "completed",
                    "totalRecords": len(tag_result),
                    "scan_time": f"{sum(result.processing_time for result in results.values()):.2f} seconds"
                },
                "tag_result": tag_result
            }

            # Handle results with retries
            await self.s3_client.upload_result(request_id, payload)
            await self.callback_handler.callback_tag_results(payload, callback_url)
        
        else:
            logger.error(f"No tag results found for request_id {request_id}")
        


    async def get_processing_status(self, request_ids: List[str]) -> List[Dict]:
        """Get processing status for multiple request IDs."""
        results = []
        
        for request_id in request_ids:
            try:
                # Check if result exists in S3
                status = self.s3_client.check_result_exists(request_id)
                results.append({
                    "request_id": request_id,
                    "status": "COMPLETED" if status else "NOT_FOUND"
                })
            except Exception as e:
                logger.error(f"Error checking status for request_id {request_id}: {e}")
                results.append({
                    "request_id": request_id,
                    "status": "ERROR"
                })
                
        return results

    async def get_processing_results(self, request_ids: List[str]) -> List[Dict]:
        """Get processing results for multiple request IDs."""
        results = []
        
        for request_id in request_ids:
            try:
                result = self.s3_client.get_result(request_id)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error fetching result for request_id {request_id}: {e}")
                continue
                
        return results

    async def process_sync(self, ucrid: str, media_url: str) -> Dict:
        """Process a single creative synchronously and return results immediately."""
        try:
            # Create creative object
            creative = {
                "ucrid": ucrid,
                "media_url": media_url
            }

            # Use existing processing method
            result = await self._process_single(creative)
            
            if result.status == 'success':
                # Format response using existing tag mapping logic
                creative_tags = []
                for tag in result.tags:
                    tag_name = tag if isinstance(tag, str) else tag.get('name', '')
                    tag_name_lower = tag_name.lower()
                    
                    creative_tags.append({
                        "id": self.tag_map.get(tag_name_lower),
                        "name": tag_name
                    })

                return {
                    "response": {
                        "ucrid": ucrid,
                        "creativeTags": creative_tags,
                        "scan_time": result.processing_time
                    }
                }
            else:
                raise Exception(result.error)
                
        except Exception as e:
            logger.error(f"Error in sync processing for UCRID {ucrid}: {e}")
            raise

            
