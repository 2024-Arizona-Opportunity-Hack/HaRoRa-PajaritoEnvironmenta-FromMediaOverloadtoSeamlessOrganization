import base64
import traceback
from urllib.parse import urlparse, urlunparse
import io
import json
import openai
import os
import uuid
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
from PIL.TiffImagePlugin import IFDRational
from typing import List
import piexif
import requests
from together import Together
from pydantic import BaseModel, Field

import structured_llm_output
from fractions import Fraction
import logging

logging.basicConfig(level=logging.INFO)


# ===
# Image Utils
# ===
def get_thumbnail(image_path: str) -> str:
    """Loads image and uses Pillow to get thumbnail of that image and return base64 url"""
    size = (128, 128)  # Thumbnail size
    with Image.open(image_path) as img:
        img.thumbnail(size)
        buffer = io.BytesIO()
        img_format = image_path.split(".")[-1].upper()
        if img_format == "JPG":
            img_format = "JPEG"
        img.save(buffer, format=img_format)
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/{img_format};base64,{img_str}"


# ===
# Tagging
# ===
class ImageData(BaseModel):
    title: str = Field(desc="Short 2-3 words title describing the image content")
    image_description: str = Field(desc="One-line caption describing what the image is about")
    tags: List[str] = Field(
        desc="List of concise tags for image retrieval, including objects, actions, settings, seasons, locations, image type, text, and distinctive features",
        max_length=20,
    )


def process_batch(files_list: list[tuple]) -> tuple[str, str, str, str]:
    batch_oai, batch_metadata = [], dict()
    for x in files_list:
        image_path = x[0]
        size = 1024
        image = Image.open(image_path)
        resized_image = image.resize((size, size))
        img_format = image_path.split(".")[-1].upper()
        if img_format == "JPG":
            img_format = "JPEG"
        output = io.BytesIO()
        resized_image.save(output, format=img_format)
        output.seek(0)
        image_url = f"data:image/{img_format};base64,{base64.b64encode(output.getvalue()).decode('utf-8')}"

        suffix = f"\n---\n\n{structured_llm_output.generate_response_prompt(ImageData)}---\n"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Analyze the image and provide a detailed, factual description. Ensure that the tags are short, specific, and relevant for search queries. Avoid redundancy and prioritize the most salient aspects of the image.\n{suffix}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": "low"},
                    },
                ],
            }
        ]
        batch_oai.append(
            json.dumps(
                {
                    "custom_id": image_path,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {"model": "gpt-4o-mini", "messages": messages, "max_tokens": 1024},
                }
            )
        )
        batch_metadata[image_path] = {
            "image_path": image_path,
            "tags": x[1],
            "access_token": x[2],
        }

    batch_uid = uuid.uuid4()
    batch_jsonl = f"/tmp/{batch_uid}.jsonl"
    batch_metadata_json = f"/tmp/{batch_uid}_metadata.json"
    with open(batch_jsonl, "w") as f:
        f.write("\n".join(batch_oai))
    with open(batch_metadata_json, "w") as f:
        json.dump(batch_metadata, f)

    client = openai.OpenAI()
    # Upload the batch file
    batch_input_file = client.files.create(file=open(batch_jsonl, "rb"), purpose="batch")
    # Create the batch job
    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        completion_window="24h",
        endpoint="/v1/chat/completions",
    )
    return batch.id, batch_input_file.id, batch_jsonl, batch_metadata_json


def get_image_captioning(image_path: str) -> dict | None:
    try:
        size = 1024
        image = Image.open(image_path)
        resized_image = image.resize((size, size))
        img_format = image_path.split(".")[-1].upper()
        if img_format == "JPG":
            img_format = "JPEG"
        output = io.BytesIO()
        resized_image.save(output, format=img_format)
        output.seek(0)
        image_url = f"data:image/{img_format};base64,{base64.b64encode(output.getvalue()).decode('utf-8')}"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze the image and provide a detailed, factual description. Ensure that the tags are short, specific, and relevant for search queries. Avoid redundancy and prioritize the most salient aspects of the image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": "low"},
                    },
                ],
            }
        ]
        response = structured_llm_output.run(
            model="gpt-4o-mini",
            messages=messages,
            max_retries=3,
            response_model=ImageData,
            temp=0.8,
        )
        result = response.model_dump()
        return result
    except Exception as e:
        print(e)
        return None

# ===
# Image Metadata Extraction
# ===
def exif_serialization(obj):
    """Handle various EXIF object types for JSON serialization."""
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')  # Convert bytes to base64 encoded string
    elif isinstance(obj, IFDRational):  # Simulating IFDRational by using fractions.Fraction
        return float(obj)  # Convert IFDRational to float
    elif isinstance(obj, dict):
        return {k: exif_serialization(v) for k, v in obj.items()}
    elif isinstance(obj, tuple):
        return tuple(exif_serialization(v) for v in obj)
    return obj

def get_exif_data(image_path: str) -> dict:
    """Extract EXIF data from an image."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()  # Retrieve EXIF data
        image.close()
        
        if exif_data is None:
            return {}
        
        exif = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif[tag_name] = value

        serializable_exif = exif_serialization(exif)
        return serializable_exif

    except FileNotFoundError:
        logging.error(f"File not found: {image_path}")
        return {}
    except IOError:
        logging.error(f"Error opening file: {image_path}")
        return {}
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return {}

def convert_to_degrees(value: tuple[float, float, float]) -> float:
    """Convert the GPS coordinates stored as (degrees, minutes, seconds) into decimal degrees."""
    try:
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)
    except ValueError:
        logging.warning(f"Invalid GPS data: {value}")
        return 0.0

def get_gps_info(exif: dict) -> dict:
    """Extract GPS information from EXIF data."""
    try:
        gps_info = {}
        if 'GPSInfo' in exif:
            for key, value in exif['GPSInfo'].items():
                decode = GPSTAGS.get(key, key)
                gps_info[decode] = value

            # Convert latitude and longitude to decimal degrees
            if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                lat_ref = gps_info.get('GPSLatitudeRef')
                lon_ref = gps_info.get('GPSLongitudeRef')

                lat = convert_to_degrees(gps_info['GPSLatitude'])
                lon = convert_to_degrees(gps_info['GPSLongitude'])

                if lat_ref != 'N':  # South latitudes are negative
                    lat = -lat
                if lon_ref != 'E':  # West longitudes are negative
                    lon = -lon

                gps_info['Latitude'] = lat
                gps_info['Longitude'] = lon

        return gps_info
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.error(f"{traceback.format_exc()}")
        return {}

def extract_image_metadata(image_path: str) -> dict:
    """
    Extract metadata including latitude, longitude, and capture date from an image.
    
    Args:
        image_path (str): Path to the image file.

    Returns:
        dict: A dictionary containing the capture date, latitude, and longitude.
    """
    img_metadata = {}

    try:
        # Attempt to extract EXIF data
        exif_data = get_exif_data(image_path)
        if not exif_data:
            logging.info("No EXIF metadata found.")
            return {}
        
        # Extract capture date
        img_metadata['capture_date'] = exif_data.get('DateTimeOriginal', None)
        
        # Extract GPS information
        gps_info = get_gps_info(exif_data)
        if gps_info:
            img_metadata['latitude'] = gps_info.get('Latitude', None)
            img_metadata['longitude'] = gps_info.get('Longitude', None)
        else:
            logging.info("No GPS information found.")

        # Include all remaining EXIF data excluding GPSInfo and DateTimeOriginal
        for key, value in exif_data.items():
                img_metadata[key] = value

    except FileNotFoundError:
        logging.error(f"File not found: {image_path}")
        return {}
    
    except IOError as io_err:
        logging.error(f"IOError occurred when processing file: {image_path}. Error: {io_err}")
        return {}
    
    except Exception as e:
        logging.error(f"An unexpected error occurred while processing the image metadata: {e}")
        return {}

    return img_metadata

# ===
# Embeddings
# ===
from typing import List
from transformers import CLIPProcessor, CLIPModel
import torch

# Initialize the model and processor
model: CLIPModel = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor: CLIPProcessor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def get_image_embedding(image_path: str) -> List[float]:
    try:
        image = Image.open(image_path)
        inputs = processor(images=image, return_tensors="pt")
        outputs = model.get_image_features(**inputs)
        return outputs[0].tolist()
    except Exception as e:
        print(e)


def get_text_embedding(text: str) -> List[float]:
    try:
        inputs = processor(text=[text], return_tensors="pt")
        outputs = model.get_text_features(**inputs)
        return outputs[0].tolist()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print("Testing the above functions")
    # image_path = "../../image.jpg"
    image_path = "/Users/saurabh/AA/divergent/ASU Graduation Ceremony/IMG_7918.JPG"
    # dropbox_img_path = "https://www.dropbox.com/sh/34kuc:re3kg4bes/AACDsAS8URMseqXl1JrXqy84a/2017/_FINAL-2017Nov18-SmallFryProspectMine-WithPatrickRowe-PHOTOS-From-Dave-Schiferl?e=2&preview=_DSC6125-Small-Fry-Prospect-Mine-Searching-For-Fluorite.JPG&st=5n2irk4w&subfolder_nav_tracking=1&dl=0"

    # Test EXIF data extraction
    print("\nTesting get_exif_data...")
    exif_data = get_exif_data(image_path)
    if exif_data:
        print("EXIF data extracted:", json.dumps(exif_data, indent=2))
    else:
        print("No EXIF data found.")

    # Test image metadata extraction
    print("\nTesting extract_image_metadata...")
    metadata = extract_image_metadata(image_path)
    if metadata:
        print("Image metadata extracted:", json.dumps(metadata, indent=2))
    else:
        print("No metadata found.")

    # Test thumbnail generation
    print("Testing get_thumbnail...")
    thumbnail = get_thumbnail(image_path)
    print("Thumbnail generated:", thumbnail[:50] + "...")

    # Test image captioning
    print("\nTesting get_image_captioning...")
    captioning_result = get_image_captioning(image_path)
    if captioning_result:
        print("Captioning result:", json.dumps(captioning_result, indent=2))
    else:
        print("Failed to generate image captioning.")

    # Test image embedding
    print("\nTesting get_image_embedding...")
    image_embedding = get_image_embedding(image_path)
    if image_embedding:
        print("Image embedding generated:", image_embedding[:5], "...")
    else:
        print("Failed to generate image embedding.")

    # Test text embedding
    print("\nTesting get_text_embedding...")
    text = "Sample text for embedding"
    text_embedding = get_text_embedding(text)
    if text_embedding:
        print("Text embedding generated:", text_embedding[:5], "...")
    else:
        print("Failed to generate text embedding.")
