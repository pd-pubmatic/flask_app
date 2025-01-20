from celery import Celery
from app.processors import audio_transcription,video_ocr,video_file_download,prompt_processing

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def process_media_url(creative, callback_url, request_id):
    try:
        # Stage 1: Download video
        video_path = video_file_download.download_video(creative['media_url'], creative['ucrid'])

        # Stage 2: Transcription
        transcription = audio_transcription.transcribe_audio(video_path)

        # Stage 3: OCR extraction
        ocr_data = video_ocr.capture_crop_frames_and_get_ocr(video_path)

        # Stage 4: Combine data
        combined_data = combine_data(transcription, ocr_data)

        # Stage 5: Callback with results
        send_callback(callback_url, {
            "metadata": {
                "request_id": request_id,
                "status": "COMPLETED",
                "totalRecords": 1
            },
            "tag_result": [{
                "ucrid": creative['ucrid'],
                "creativeTags": combined_data
            }]
        })

    except Exception as e:
        # Handle errors and send failure callback
        send_callback(callback_url, {
            "metadata": {
                "request_id": request_id,
                "status": "FAILED",
                "totalRecords": 0
            },
            "error": str(e)
        })
