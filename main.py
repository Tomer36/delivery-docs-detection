import sys
import time
import cv2
import pytesseract
import re
import os
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image


def load_image(image_path):
    print(f"Loading image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
    else:
        print(f"Image loaded successfully: {image_path}")
    return image


def extract_text_from_image(image):
    print("Converting image to grayscale")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("Extracting text using Tesseract")
    text = pytesseract.image_to_string(gray, lang='heb+eng', config='--psm 6')
    print(f"Extracted text: {text}")
    return text


def find_seven_digit_number(text):
    print("Searching for seven-digit number in text")
    pattern = r'\b(?!9865566|9862065)(\d{7})\b'
    match = re.search(pattern, text)
    if match:
        number = match.group(1)
        print(f"Found seven-digit number: {number}")
        if number.startswith("0"):  # Check if the number starts with 0
            number = number[1:]  # Remove the first digit
            print(f"Removed leading zero, updated number: {number}")
        return number
    else:
        print("No valid seven-digit number found")
        return None


def detect_and_extract_number(image_path):
    image = load_image(image_path)
    if image is not None:
        text = extract_text_from_image(image)
        number = find_seven_digit_number(text)
        return number
    else:
        print("No image to process")
        return None


def compress_image(input_path, output_path, quality=30, resize_factor=0.5):
    """
    Compress and resize an image.

    Parameters:
    input_path (str): Path to the input image file.
    output_path (str): Path to save the compressed image file.
    quality (int): Quality of the output image (1 to 95). Default is 30.
    resize_factor (float): Factor by which to resize the image. Default is 0.5 (50% of original size).
    """
    with Image.open(input_path) as img:
        # Resize image if resize_factor is less than 1.0
        if resize_factor < 1.0:
            new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Save the image with the desired quality
        img.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)


def process_image(image_path, output_folder):
    extracted_number = detect_and_extract_number(image_path)
    if extracted_number:
        print(f"Extracted Number from {image_path}: {extracted_number}")
        new_filename = extracted_number + ".jpg"  # Rename the file with the extracted number
        output_path = os.path.join(output_folder, new_filename)

        # Compress and save the image
        try:
            compress_image(image_path, output_path, quality=30, resize_factor=0.5)
            os.remove(image_path)  # Remove the original file after compression
            print(f"Moved and compressed file {image_path} to {new_filename}")
        except Exception as e:
            print(f"Failed to move and compress file {image_path} to {output_path}: {e}")
    else:
        print(f"No number found in {image_path}.")


class ImageEventHandler(FileSystemEventHandler):
    def __init__(self, output_folder):
        self.output_folder = output_folder

    def on_created(self, event):
        if not event.is_directory:
            if event.src_path.lower().endswith((".jpg", ".png")):
                print(f"New file detected: {event.src_path}")
                time.sleep(1)  # Wait a bit for the file to be fully written
                process_image(event.src_path, self.output_folder)
            else:
                print(f"Skipping non-image file: {event.src_path}")


def process_images_in_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".jpg", ".png")):  # Adjust file extensions as needed
            image_path = os.path.join(input_folder, filename)
            print(f"Processing file: {filename}")
            process_image(image_path, output_folder)
        else:
            print(f"Skipping non-image file: {filename}")


def main():
    parser = argparse.ArgumentParser(description='Process and compress images from a folder.')
    parser.add_argument('input_folder', type=str, help='Path to the input folder')
    parser.add_argument('output_folder', type=str, help='Path to the output folder')
    parser.add_argument('tesseract_path', type=str, help='Path to the Tesseract executable')
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    tesseract_path = args.tesseract_path

    # Set the Tesseract executable path
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Process existing files in the input folder
    process_images_in_folder(input_folder, output_folder)

    # Set up the watchdog observer to monitor the input folder
    event_handler = ImageEventHandler(output_folder)
    observer = Observer()
    observer.schedule(event_handler, input_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
