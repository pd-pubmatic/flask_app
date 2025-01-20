d =         {"ucrid":"595744123519430565","media_url":"aHR0cHM6Ly92aWRlby5zdGFja2FkYXB0LmNvbS90cmFuc2NvZGVkL2NyZWF0aXZlcy8yMzQ2Ni9jNGU4MWE2YmY4YmJmNGUwZTVlYzE2MGNmNDM5MjAxOS5tcDRfMTYwMDIwNzg5MjMwNS0zM3VmYTVfMTkyMHgxMDgwQDMwMDBrYnBzLm1wNA=="
             
             ,
                 "ucrid":"59574412351905675","media_url":"aHR0cHM6Ly92aWRlby5zdGFja2FkYXB0LmNvbS90cmFuc2NvZGVkL2NyZWF0aXZlcy8yMzQ2Ni9jNGU4MWE2YmY4YmJmNGUwZTVlYzE2MGNmNDM5MjAxOS5tcDRfMTYwMDIwNzg5MjMwNS0zM3VmYTVfMTkyMHgxMDgwQDMwMDBrYnBzLm1wNA=="
             ,
             "ucrid":"59574412394305675","media_url":"aHR0cHM6Ly92aWRlby5zdGFja2FkYXB0LmNvbS90cmFuc2NvZGVkL2NyZWF0aXZlcy8yMzQ2Ni9jNGU4MWE2YmY4YmJmNGUwZTVlYzE2MGNmNDM5MjAxOS5tcDRfMTYwMDIwNzg5MjMwNS0zM3VmYTVfMTkyMHgxMDgwQDMwMDBrYnBzLm1wNA=="
             ,
             "ucrid":"5941235194305675","media_url":"aHR0cHM6Ly92aWRlby5zdGFja2FkYXB0LmNvbS90cmFuc2NvZGVkL2NyZWF0aXZlcy8yMzQ2Ni9jNGU4MWE2YmY4YmJmNGUwZTVlYzE2MGNmNDM5MjAxOS5tcDRfMTYwMDIwNzg5MjMwNS0zM3VmYTVfMTkyMHgxMDgwQDMwMDBrYnBzLm1wNA==",
             "ucrid":"5","media_url":"aHR0cHM6Ly92aWRlby5zdGFja2FkYXB0LmNvbS90cmFuc2NvZGVkL2NyZWF0aXZlcy8yMzQ2Ni9jNGU4MWE2YmY4YmJmNGUwZTVlYzE2MGNmNDM5MjAxOS5tcDRfMTYwMDIwNzg5MjMwNS0zM3VmYTVfMTkyMHgxMDgwQDMwMDBrYnBzLm1wNA=="
             
             }


def process_media_url(creative, callback_url, request_id):
    try:
        # Stage 1: Download video
        video_path = video_file_deownload.download_video(creative['media_url'], creative['ucrid'])

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
        })e