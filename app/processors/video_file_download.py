import requests

def download_video(media_url, ucrid):
    # Download video from media_url
    video_path = f"app/resources{ucrid}.mp4"
    response = requests.get(media_url, stream=True)
    with open(video_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return video_path