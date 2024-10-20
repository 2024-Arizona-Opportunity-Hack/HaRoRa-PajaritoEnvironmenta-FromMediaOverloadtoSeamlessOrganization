import io
import os
import json
import base64
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
from typing import List
from pydantic import BaseModel, Field

import structured_llm_output


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


def get_image_captioning(image_path: str) -> str | None:
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
def get_exif_data(image_path: str) -> dict | None:
    """Extract EXIF data from an image."""
    image = Image.open(image_path)
    exif_data = image._getexif()  # Retrieve EXIF data
    if exif_data is None:
        return None
    exif = {}
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        exif[tag_name] = value
    return exif


def get_gps_info(exif):
    """Extract GPS information from EXIF data."""
    gps_info = {}
    if "GPSInfo" in exif:
        for key in exif["GPSInfo"].keys():
            decode = GPSTAGS.get(key, key)
            gps_info[decode] = exif["GPSInfo"][key]

        # Convert latitude and longitude to decimal degrees
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat_ref = gps_info.get("GPSLatitudeRef")
            lon_ref = gps_info.get("GPSLongitudeRef")

            lat = convert_to_degrees(gps_info["GPSLatitude"])
            lon = convert_to_degrees(gps_info["GPSLongitude"])

            if lat_ref != "N":  # South latitudes are negative
                lat = -lat
            if lon_ref != "E":  # West longitudes are negative
                lon = -lon

            gps_info["Latitude"] = lat
            gps_info["Longitude"] = lon

    return gps_info


def convert_to_degrees(value: tuple[float, float, float]) -> float:
    """Convert the GPS coordinates stored as (degrees, minutes, seconds) into decimal degrees."""
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)


def extract_image_metadata(image_path: str):
    """Extract metadata including latitude, longitude, and capture date."""
    img_metadata = {}
    exif_data = get_exif_data(image_path)
    if not exif_data:
        print("No EXIF metadata found.")
        return
    img_metadata["capture_date"] = exif_data.get("Date/TimeOriginal", None)
    gps_info = get_gps_info(exif_data)
    if gps_info:
        img_metadata["latitude"] = gps_info.get("Latitude", None)
        img_metadata["longitude"] = gps_info.get("Longitude", None)
    else:
        print("No GPS information found.")
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
    image_path = "../../image.jpg"

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
