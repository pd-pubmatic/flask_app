import pandas as pd
import easyocr
import cv2
from PIL import Image
import os
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)
input_folder_path="app/resources"

async def capture_crop_frames_and_get_ocr(filename: str):
    try:
        video_file_path = os.path.join(input_folder_path, filename)
        cap = cv2.VideoCapture(video_file_path)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / frame_rate

        # Times to capture frames: last 0.5 sec, 1 sec, and 2 sec
        capture_times = [duration - 0.5, duration - 1, duration - 2]

        top_frame_ocr_list = []
        bottom_frame_ocr_list = []
        
        for t in capture_times:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)  # Set to the specific time
            success, frame = cap.read()
            if success:
                # Process the frame directly for OCR
                top_ocr, bottom_ocr = crop_image(frame)
                top_frame_ocr_list.append(top_ocr)
                bottom_frame_ocr_list.append(bottom_ocr)
            else:
                print(f"Failed to capture frame at {t} seconds")

        cap.release()
        logger.info(f"OCR Data for {filename}: {top_frame_ocr_list}, {bottom_frame_ocr_list}")
        return top_frame_ocr_list, bottom_frame_ocr_list
    except Exception as e:
        logger.error(f"Error processing OCR for {filename}: {e}")
        raise RuntimeError(f"Error processing OCR for {filename}: {e}")

def crop_image(frame):
    """
    Crops the given frame into two parts:
    - Top 80% portion
    - Bottom 20% portion
    Performs OCR on both parts and returns the results.
    """
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) 
    width, height = img.size

    # Define crop areas
    top_box = (0, 0, width, int(height * 0.8))  # Top 80%
    bottom_box = (0, int(height * 0.8), width, height)  # Bottom 20%

    # Crop the image
    top_img = img.crop(top_box)
    bottom_img = img.crop(bottom_box)
    
    # Convert PIL images to numpy arrays directly
    top_np_array = np.array(top_img)
    bottom_np_array = np.array(bottom_img)

    # Perform OCR
    top_ocr_result = perform_ocr(top_np_array)
    bottom_ocr_result = perform_ocr(bottom_np_array)

    return top_ocr_result, bottom_ocr_result

def perform_ocr(img):
    """
    Performs OCR on the given image and returns the extracted text as a single string.
    """
    ocr_result = reader.readtext(img, detail=0)  # Extract text only
    return " ".join(ocr_result)
