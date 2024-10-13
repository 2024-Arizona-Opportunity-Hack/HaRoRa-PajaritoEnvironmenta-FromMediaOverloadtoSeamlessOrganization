import io
import os
import base64
import replicate
from PIL.ExifTags import TAGS
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

        # response = client.chat.completions.create(
        #     model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        #     temperature=0.3,
        #     messages=messages)
        # result = response.choices[0].message.content
        response = structured_llm_output.run(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=messages,
            max_retries=3,
            response_model=ImageData,
        )

        return response.json()
    except Exception as e:
        print(e)

def get_image_embedding(image_path: str):
  try:
    image = open(image_path, "rb")
    output = replicate.run(
      "andreasjansson/clip-features:75b33f253f7714a281ad3e9b28f63e3232d583716ef6718f2e46641077ea040a",
      input={
          "inputs": image
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
  except Exception as e:
    print(e)
  
def extract_image_metadata(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Extract EXIF data
        exif_data = img._getexif()
        
        # If there's no EXIF data, return empty
        if exif_data is None:
            return "No EXIF metadata found"
        
        # Create a dictionary to store metadata
        metadata = {}
        
        # Loop through all EXIF tags and convert them to readable tags
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            metadata[tag_name] = value
        
        return metadata

if __name__ == "__main__":
    extract_image_metadata("/Users/saurabh/Downloads/DSC01280 (1).jpg")
#   get_image_captioning("/Users/saurabh/Downloads/PEECJillian_photo.jpg")
  #get_image_captioning("https://www.dropbox.com/sh/34kuc:re3kg4bes/AACDsAS8URMseqXl1JrXqy84a/2017/_FINAL-2017Nov18-SmallFryProspectMine-WithPatrickRowe-PHOTOS-From-Dave-Schiferl?e=2&preview=_DSC6125-Small-Fry-Prospect-Mine-Searching-For-Fluorite.JPG&st=5n2irk4w&subfolder_nav_tracking=1&dl=0")