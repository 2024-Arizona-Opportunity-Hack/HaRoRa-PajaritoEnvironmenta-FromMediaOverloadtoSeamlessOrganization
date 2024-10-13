import io
import os
import json
import base64
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
from typing import List
from together import Together
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import structured_llm_output

class ImageData(BaseModel):
    title: str = Field(desc="Short filename-like title describing the image content")
    image_description: str = Field(desc="One-line caption describing what the image is about")
    tags: List[str] = Field(desc="List of concise tags for image retrieval, including objects, actions, settings, seasons, locations, image type, text, and distinctive features", max_length=20)
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
    
    return img_metadata

if __name__ == "__main__":
    image_path = "/Users/saurabh/AA/divergent/ASU Graduation Ceremony/IMG_7918.JPG"
    dropbox_img_path = "https://www.dropbox.com/sh/34kuc:re3kg4bes/AACDsAS8URMseqXl1JrXqy84a/2017/_FINAL-2017Nov18-SmallFryProspectMine-WithPatrickRowe-PHOTOS-From-Dave-Schiferl?e=2&preview=_DSC6125-Small-Fry-Prospect-Mine-Searching-For-Fluorite.JPG&st=5n2irk4w&subfolder_nav_tracking=1&dl=0"
    # print(get_text_embedding("A couple walking hand in hand on a beach during sunset"))
    # print(get_image_captioning(image_path))
    # print(extract_image_metadata(image_path))
    # get_image_captioning(dropbox_img_path)
