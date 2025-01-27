import speech_recognition as sr
import os
from moviepy.editor import VideoFileClip
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Initialize the speech recognizer once as a global instance
recognizer = sr.Recognizer()
recognizer.energy_threshold = 500

input_folder_path="app/resources"

# Function to extract audio from a video file
def extract_audio_from_video(video_path, audio_output_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_output_path)

# Process each video file in the input folder
async def transcribe_audio(filename: str) -> str:
    if filename.endswith(".mp4"):  # Adjust the file extension as needed
        video_path = os.path.join(input_folder_path, filename)
        audio_path = os.path.splitext(video_path)[0] + ".wav"

    try:
        extract_audio_from_video(video_path, audio_path)
        
        # Use the global recognizer instance instead of creating a new one
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio)
        
        logger.info(f"Transcription for {filename}: {transcription}")
        return transcription
        
    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}")
        raise RuntimeError(f"Error processing file {filename}: {e}")

