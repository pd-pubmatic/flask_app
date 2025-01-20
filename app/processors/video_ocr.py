import pandas as pd
import easyocr
import cv2
from PIL import Image

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

def capture_crop_frames_and_get_ocr(video_file_path):
    """
    Captures frames at specific times in a video, crops them, and performs OCR.
    Returns OCR results for the top and bottom portions of the frames.
    """
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
    return top_frame_ocr_list, bottom_frame_ocr_list

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
    top_box = (0, 0, width, int(height * 0.8))  # Top 70%
    bottom_box = (0, int(height * 0.8), width, height)  # Bottom 30%

    # Crop and perform OCR
    top_img = img.crop(top_box)
    bottom_img = img.crop(bottom_box)

    top_ocr_result = perform_ocr(top_img)
    bottom_ocr_result = perform_ocr(bottom_img)

    return top_ocr_result, bottom_ocr_result

def perform_ocr(img):
    """
    Performs OCR on the given image and returns the extracted text as a single string.
    """
    ocr_result = reader.readtext(img, detail=0)  # Extract text only
    return " ".join(ocr_result)
