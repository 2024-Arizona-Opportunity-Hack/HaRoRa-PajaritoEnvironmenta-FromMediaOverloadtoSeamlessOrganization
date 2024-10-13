import io
import os
import json
import base64
from urllib.parse import urlparse, urlunparse
import replicate
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
from typing import List
import requests
from together import Together
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import structured_llm_output

class ImageData(BaseModel):
    title: str = Field(desc="Short filename-like title describing the image content")
    image_description: str = Field(desc="One-line caption describing what the image is about")
    tags: List[str] = Field(desc="List of concise tags for image retrieval, including objects, actions, settings, seasons, locations, image type, text, and distinctive features", max_length=10)
    class Config:
        schema_extra = {
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
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_vision_response(prompt: str, image_path: str):
    try:
        client = Together()
        messages = [{"role": "user", "content": []}]
        
        if prompt:
            messages[0]["content"].append({"type": "text", "text": prompt})
        
        if image_path:
            messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": { "url": f"data:image/jpeg;base64,{resize_and_encode_image(image_path)}" },
                })
        response = structured_llm_output.run(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=messages,
            max_retries=3,
            response_model=ImageData,
            temp=0.7
        )

        result = json.loads(response.model_dump_json())
        return result
    except Exception as e:
        print(e)

def get_image_embedding(image_path: str):
  try:
    image = get_image(image_path)
    output = replicate.run(
      "andreasjansson/clip-features:75b33f253f7714a281ad3e9b28f63e3232d583716ef6718f2e46641077ea040a",
      input={
          "inputs": image
      }
      )
    return output[0]['embedding']
  except Exception as e:
    print(e)

def get_text_embedding(text: str):
  try:
    output = replicate.run(
      "andreasjansson/clip-features:75b33f253f7714a281ad3e9b28f63e3232d583716ef6718f2e46641077ea040a",
      input={
          "inputs": text
      }
      )
    return output[0]['embedding']
  except Exception as e:
    print(e)

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

def get_exif_data(image_path):
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
    if 'GPSInfo' in exif:
        for key in exif['GPSInfo'].keys():
            decode = GPSTAGS.get(key, key)
            gps_info[decode] = exif['GPSInfo'][key]

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

def convert_to_degrees(value):
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

    img_metadata['capture_date'] = exif_data.get('Date/TimeOriginal', None)

    gps_info = get_gps_info(exif_data)

    
    if gps_info:
        img_metadata['latitude'] = gps_info.get('Latitude', None)
        img_metadata['longitude'] = gps_info.get('Longitude', None)
    else:
        print("No GPS information found.")

    print("Other EXIF metadata:")
    for key, value in exif_data.items():
        img_metadata[key] = value
    
    return img_metadata

if __name__ == "__main__":
    image_path = "/Users/saurabh/AA/divergent/ASU Graduation Ceremony/IMG_7918.JPG"
    dropbox_img_path = "https://www.dropbox.com/sh/34kuc:re3kg4bes/AACDsAS8URMseqXl1JrXqy84a/2017/_FINAL-2017Nov18-SmallFryProspectMine-WithPatrickRowe-PHOTOS-From-Dave-Schiferl?e=2&preview=_DSC6125-Small-Fry-Prospect-Mine-Searching-For-Fluorite.JPG&st=5n2irk4w&subfolder_nav_tracking=1&dl=0"
    # print(get_text_embedding("A couple walking hand in hand on a beach during sunset"))
    print(get_image_embedding(dropbox_img_path))
    # print(extract_image_metadata(image_path))
    # get_image_captioning(dropbox_img_path)
