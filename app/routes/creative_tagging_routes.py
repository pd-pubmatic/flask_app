from flask import request, jsonify, Blueprint
import logging
import asyncio
import threading

creative_tagging = Blueprint('creative_tagging', __name__)

from app.services import creative_tagging_service

logger = logging.getLogger(__name__)

@creative_tagging.route("/public/api/v1/creative-tags-automation/tag/run", methods=["POST"])
def run_tagging_for_media_urls():
    data = request.get_json()

    callback_url = data.get("callback_url")
    request_id = data.get("request_id")
    creatives = data.get("creatives", [])

    logger.info("Received request for tagging media URLs")
    logger.debug(f"Callback URL: {callback_url}, Request ID: {request_id}, Creatives: {creatives}")

    def background_task():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            creative_tagging_service.process_media_url(creatives, callback_url, request_id)
        )
        loop.close()

    # Run the processing in a background thread
    threading.Thread(target=background_task).start()

    return jsonify({
        "message": "Processing started",
        "request_id": request_id
    }), 202

@creative_tagging.route("/public/api/v1/dev-tags-automation/status/run", methods=["POST"])
async def check_processing_status():
    data = request.get_json()
    request_ids = data.get("request_ids", [])
    
    if not request_ids:
        return jsonify({
            "response": [],
            "message": "No request IDs provided"
        }), 400

    service = creative_tagging_service.CreativeTaggingService()
    results = await service.get_processing_status(request_ids)

    return jsonify({
        "response": results
    }), 200

@creative_tagging.route("/public/api/v1/creative-tags-automation/get/run", methods=["POST"])
async def get_processing_results():
    data = request.get_json()
    request_ids = data.get("request_ids", [])
    
    if not request_ids:
        return jsonify({
            "response": [],
            "message": "No request IDs provided"
        }), 400

    service = creative_tagging_service.CreativeTaggingService()
    results = await service.get_processing_results(request_ids)

    return jsonify({
        "response": results
    }), 200

@creative_tagging.route("/public/api/v1/creative-tags/sync/run", methods=["POST"])
async def run_tagging_sync():
    data = request.get_json()
    ucrid = data.get("ucrid")
    media_url = data.get("media_url")

    if not ucrid or not media_url:
        return jsonify({
            "error": "Missing required fields: ucrid or media_url"
        }), 400

    service = creative_tagging_service.CreativeTaggingService()
    
    try:
        result = await service.process_sync(ucrid, media_url)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error processing sync request: {e}")
        return jsonify({
            "error": str(e)
        }), 500