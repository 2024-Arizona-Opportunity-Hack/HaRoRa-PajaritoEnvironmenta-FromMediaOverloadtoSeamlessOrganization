import io
import os
import json
import base64
import traceback
from urllib.parse import urlparse, urlunparse
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
from PIL.TiffImagePlugin import IFDRational
from typing import List
import piexif
import requests
from together import Together
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import structured_llm_output
from fractions import Fraction
import logging

logging.basicConfig(level=logging.INFO)

class ImageData(BaseModel):
    title: str = Field(desc="Short filename-like title describing the image content")
    image_description: str = Field(desc="One-line caption describing what the image is about")
    tags: List[str] = Field(desc="List of concise tags for image retrieval, including objects, actions, settings, seasons, locations, image type, text, and distinctive features", max_length=20)
    class Config:
        json_schema_extra = {
            "example": {
                "title": "sunset_beach_couple.jpg",
                "image_description": "A couple walking hand in hand on a beach during sunset",
                "tags": [
                    "beach", "sunset", "couple", "romantic", "walking",
                    "ocean", "sand", "silhouette", "evening", "vacation",
                    "tropical", "landscape", "outdoor", "nature", "coastline"
                ]
            }
        }

IMAGE_CAPTIONING_PROMPT = """Analyze the image and provide a detailed, factual description. Ensure that the tags are short, specific, and relevant for search queries. Avoid redundancy and prioritize the most salient aspects of the image.
focusing on the following aspects:
{format_instructions} """

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def convert_to_raw_url(url):
    # Parse the URL into components
    parsed_url = urlparse(url)
    
    # Rebuild the URL without query parameters and add ?raw=1
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return new_url + "?raw=1"

def download_image(url):
    if 'dropbox' in url:
        url = convert_to_raw_url(url)
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception("Failed to download image")

def get_image(image_path: str):
    if is_url(image_path):
        image = download_image(image_path)
    else:
        return open(image_path, "rb")
    
def resize_and_encode_image(image_path, max_size=(1024, 1024)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        buffered = io.BytesIO()
        img.save(buffered, format=img.format)
        return f"data:image/{img.format};base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

def get_vision_response(prompt: str, image_path: str):
    try:
        client = Together()
        messages = [{"role": "user", "content": []}]
        
        if prompt:
            messages[0]["content"].append({"type": "text", "text": prompt})
        
        if image_path:
            messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": { "url": resize_and_encode_image(image_path) },
                })
        response = structured_llm_output.run(
            model="gpt-4o-mini",
            messages=messages,
            max_retries=3,
            response_model=ImageData,
            temp=0.8
        )

        result = json.loads(response.model_dump_json())
        return result
    except Exception as e:
        print(e)


from typing import List
from transformers import CLIPProcessor, CLIPModel
import torch

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

# Initialize the model and processor
model: CLIPModel = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor: CLIPProcessor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_image_captioning(image_path: str):
  try:
    client = Together()
    json_parser = JsonOutputParser(pydantic_object=ImageData)
    prompt = PromptTemplate(
       template=IMAGE_CAPTIONING_PROMPT, 
       partial_variables={"format_instructions": json_parser.get_format_instructions()}
       ).format()
    
    response = get_vision_response(prompt=prompt, image_path=image_path)
    return response
  except Exception as e:
    print(e)

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

        return exif

    except FileNotFoundError:
        logging.error(f"File not found: {image_path}")
        return {}
    except IOError:
        logging.error(f"Error opening file: {image_path}")
        return {}
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return {}

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

def convert_to_degrees(value: tuple) -> float:
    """Convert the GPS coordinates stored as (degrees, minutes, seconds) into decimal degrees."""
    try:
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)
    except ValueError:
        logging.warning(f"Invalid GPS data: {value}")
        return 0.0

def convert_custom(obj):
    """Handle various EXIF object types for JSON serialization."""
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')  # Convert bytes to base64 encoded string
    elif isinstance(obj, IFDRational):  # Simulating IFDRational by using fractions.Fraction
        return float(obj)  # Convert IFDRational to float
    elif isinstance(obj, dict):
        return {k: convert_custom(v) for k, v in obj.items()}
    elif isinstance(obj, tuple):
        return tuple(convert_custom(v) for v in obj)
    return obj

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
        raw_exif_data = get_exif_data(image_path)
        if not raw_exif_data:
            logging.info("No EXIF metadata found.")
            return {}

        exif_data = convert_custom(raw_exif_data)
        
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

if __name__ == "__main__":
    # image_path = "/Users/saurabh/Downloads/IMG_4119.jpg"
    image_path = "/Users/saurabh/AA/divergent/ASU Graduation Ceremony/IMG_7918.JPG"
    dropbox_img_path = "https://www.dropbox.com/sh/34kuc:re3kg4bes/AACDsAS8URMseqXl1JrXqy84a/2017/_FINAL-2017Nov18-SmallFryProspectMine-WithPatrickRowe-PHOTOS-From-Dave-Schiferl?e=2&preview=_DSC6125-Small-Fry-Prospect-Mine-Searching-For-Fluorite.JPG&st=5n2irk4w&subfolder_nav_tracking=1&dl=0"
    # print(get_text_embedding("A couple walking hand in hand on a beach during sunset"))
    # print(get_image_embedding(dropbox_img_path))
    dd = extract_image_metadata(image_path)
    print(json.dumps(dd, indent=4))
    # get_image_captioning(dropbox_img_path)
