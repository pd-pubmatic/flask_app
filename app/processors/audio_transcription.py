import speech_recognition as sr
import os
from moviepy.editor import VideoFileClip
import pandas as pd

# Initialize the speech recognizer
r = sr.Recognizer()
r.energy_threshold = 500

input_folder_path="app/resources"

# Function to extract audio from a video file
def extract_audio_from_video(video_path, audio_output_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_output_path)

# Process each video file in the input folder
def transcribe_audio(filename):
    
        if filename.endswith(".mp4"):  # Adjust the file extension as needed
            video_path = os.path.join(input_folder_path, filename)
            audio_path = os.path.splitext(video_path)[0] + ".wav"

        try:
            # Extract audio from the video file
            extract_audio_from_video(video_path, audio_path)
            
            # Recognize speech from the extracted audio
            with sr.AudioFile(audio_path) as source:
                audio = r.record(source)
            transcription = r.recognize_google(audio)
        
            return transcription;
        
        except Exception as e:
            print(f"Error processing file {filename}: {e}")

