from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
import imghdr
import json
from queue import Queue

app = FastAPI()
file_queue = Queue()

# Allow Cross-Origin Resource Sharing (CORS)
origins = [
    "http://localhost",
    "http://localhost:5173",  # example frontend
    "http://peec.harora.lol"  # replace with your frontend domain
    "https://peec.harora.lol"  # replace with your frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Dummy data
data = {
    "files": [],
    "tags": {}
}

# Helper function to validate image file types
def validate_image(file: UploadFile):
    valid_image_formats = {"jpeg", "png", "gif", "bmp", "jpg"}
    # Check the file type using the imghdr module
    file_type = imghdr.what(file.file)
    if file_type not in valid_image_formats:
        raise HTTPException(status_code=400, detail="Invalid image format")
    return file_type



@app.post("/upload")
async def upload_images(files: List[UploadFile] = File(...), tags: str | None = Form(...)) -> dict:
    uploaded_files: List[dict] = []
    for file in files:
        try:
            file_type: str = validate_image(file)
        except HTTPException as e:
            return e.detail

        file_id: str = str(uuid.uuid4())
        file_data: dict = {"id": file_id, "name": file.filename, "type": file_type, "tags": tags}
        data["files"].append(file_data)
        uploaded_files.append({"file_id": file_id, "name": file.filename, "type": file_type, "tags": tags})

        # store the file in /tmp dir
        file_location = f"/tmp/{file_id}.{file_type}"
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
        file_queue.put(file_location)

    # Store tags
    for tag in tags.split(","):
        tag = tag.strip()
        if tag in data["tags"]:
            data["tags"][tag].append(file_id)
        else:
            data["tags"][tag] = [file_id]

    return {"uploaded_files": uploaded_files}


import requests
# Geocoding function
def get_coordinates(location):
  api_url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
  response = requests.get(api_url)
  data = response.json()
  if data:
    return float(data[0]['lat']), float(data[0]['lon'])
  return None, None


# GET /search
import search as search_expander
@app.get("/search")
async def search_files(query: str = None):
  if query:
    search_args = search_expander.get_search_args(query)

    # geo args
    if search_args.location is not None:
      coords = get_coordinates(search_args.location)
      distance_radius = 25_000 # 25km
    else:
      coords = None
      distance_radius = None

    query_embedding = image_processor.get_text_embedding(query)
    results = db.get_search_query_result(
      query,
      query_embedding,
      search_args.season,
      ','.join(search_args.tags),
      coords,
      distance_radius,
      search_args.date_from,
      search_args.date_to,
      match_count=50,
    )
    if results is not None:
      results = [
        dict(url=x.url, title=x.title, caption=x.caption, tags=x.tags.split(','), season=x.season, uuid=x.uuid)
        for x in results
      ]
    else:
      results = []
    return {"results": results}
  else:
    return {"results": []}

# GET /tag/{uuid}
@app.get("/tag/{file_id}")
async def get_tags(file_id: str):
    tags = data["tags"].get(file_id, [])
    return {"file_id": file_id, "tags": tags}

# PUT /tag/{uuid}
@app.put("/tag/{file_id}")
async def update_tags(file_id: str, tags: List[str]):
    data["tags"][file_id] = tags
    return {"message": "Tags updated successfully", "file_id": file_id, "tags": tags}


# ===
# File Processing
# ===
import data_models
import db
import threading
import time
import process as image_processor
from datetime import datetime



def process_file(file_path: str):
  # Simulate file processing delay
  url = file_path # TODO: change to dropbox url 

  print('Getting title, caption, and tags ...')
  while True:
    img_details = image_processor.get_image_captioning(file_path)
    if img_details is None:
      print('get_image_captioning returned None')
      continue
    title = img_details['title']
    caption = img_details['image_description']
    tags = ','.join(img_details['tags'])
    break

  print('Getting image embeddings ...')
  while True:
    embedding_vector = image_processor.get_image_embedding(file_path)
    if embedding_vector is None:
      print('get image embedding returned None')
      continue
    break

  # extract_image_metadata
  print('Extracting metadata from image ...')
  img_metadata = image_processor.extract_image_metadata(file_path)
  coords = None
  capture_time_str = None
  season = None
  if img_metadata:
    lat = img_metadata.get('latitude', None)
    long = img_metadata.get('longitude', None)
    if lat is not None and long is not None: coords = [lat, long]

    capture_time = img_metadata['capture_date']
    if capture_time is not None:
      capture_time = datetime.strptime(capture_time, "%Y:%m:%d %H:%M:%S")
      capture_time_str = dt.strftime("%d/%m/%Y")
      # based on month get season as either summer, fall, winter, spring
      month = capture_time.month
      if month in [12, 1, 2]: season = 'winter'
      elif month in [3, 4, 5]: season = 'spring'
      elif month in [6, 7, 8]: season = 'summer'
      else: season = 'fall'
  img_details = db.insert(
    url=url,
    title=title,
    caption=caption,
    tags=tags,
    embedded_vector=embedding_vector,
    coordinates=coords,
    capture_time=capture_time_str,
    extended_meta=json.dumps(img_metadata) if img_metadata else None,
    season=season,
  )
  print(f"Processed file: {file_path}")
  # TODO: push file to dropbox
  # TODO: remove file

def file_processor():
  while True:
    if not file_queue.empty():
      file_path = file_queue.get()
      process_file(file_path)
    else:
      time.sleep(1)

# Start a background thread for processing files
threading.Thread(target=file_processor, daemon=True).start()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('api:app', host='localhost', port=8080, reload=True)

