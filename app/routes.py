from flask import Blueprint, jsonify, request
from app.processors import audio_transcription, media_urls, video_files, video_ocr

main = Blueprint("main", __name__)


from flask import Blueprint, request, jsonify
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/public/api/v1/creative-tags-automation/tag/run", methods=["POST"])
def run_tags():
    data = request.get_json()

    # Mocked processing logic
    callback_url = data.get("callback_url")
    request_id = data.get("request_id")
    creatives = data.get("creatives", [])

    tag_result = []
    for creative in creatives:
        ucrid = creative.get("ucrid")
        tag_result.append({
            "ucrid": ucrid,
            "creativeTags": [
                {"id": 1, "name": "Tag1"},
                {"id": 2, "name": "Tag2"}
            ]
        })

    response = {
        "metadata": {
            "request_id": request_id,
            "status": "SUCCESS",
            "totalRecords": len(creatives),
            "scan_time": datetime.utcnow().isoformat()
        },
        "tag_result": tag_result
    }

    return jsonify(response)
