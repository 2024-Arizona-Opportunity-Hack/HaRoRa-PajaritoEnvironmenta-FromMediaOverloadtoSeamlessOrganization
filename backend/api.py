# main.py

import os
import uuid
import imghdr
import json
from queue import Queue
import requests
from typing import List
from urllib.parse import urlencode

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse

# Initialize the FastAPI app
app = FastAPI()
file_queue = Queue()

# Allow Cross-Origin Resource Sharing (CORS)
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://peec.harora.lol",
    "https://peec.harora.lol",
    "http://127.0.0.1:5173",
    "https://www.dropbox.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Add session middleware for handling sessions
app.add_middleware(
    SessionMiddleware, secret_key=os.environ['FASTAPI_SESSION_SECRET_KEY']
)

# Dummy data storage
data = {
    "files": [],
    "tags": {},
}

# Dropbox OAuth Configuration
AUTH_URI = "https://www.dropbox.com/oauth2/authorize"
TOKEN_URI = "https://api.dropboxapi.com/oauth2/token"
CLIENT_URL = 'http://localhost:5173'  # Update with your client URL

# Helper function to validate image file types
def validate_image(file: UploadFile):
    valid_image_formats = {"jpeg", "png", "gif", "bmp", "jpg"}
    # Check the file type using the imghdr module
    file_type = imghdr.what(file.file)
    if file_type not in valid_image_formats:
        raise HTTPException(status_code=400, detail="Invalid image format")
    return file_type

# === Dropbox Integration Routes ===

@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth_dropbox_callback')
    auth_params = {
        "client_id": os.environ['DROPBOX_CLIENT_ID'],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "token_access_type": "offline",
    }
    auth_url = f"{AUTH_URI}?{urlencode(auth_params)}"
    return {'auth_url': auth_url}

@app.get('/auth/dropbox/callback')
async def auth_dropbox_callback(request: Request):
    auth_code = request.query_params.get('code')
    if not auth_code:
        return HTMLResponse('<h1>Authorization code not found</h1>', status_code=400)
    redirect_uri = request.url_for('auth_dropbox_callback')
    try:
        token_data = {
            "code": auth_code,
            "grant_type": "authorization_code",
            "client_id": os.environ['DROPBOX_CLIENT_ID'],
            "client_secret": os.environ['DROPBOX_CLIENT_SECRET'],
            "redirect_uri": redirect_uri,
        }
        token_response = requests.post(TOKEN_URI, data=token_data)
        token_response_data = token_response.json()

        access_token = token_response_data['access_token']
        refresh_token = token_response_data.get('refresh_token')

        # Fetch user information
        user_info_response = requests.post(
            'https://api.dropboxapi.com/2/users/get_current_account',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_info_response.json()

        request.session['user'] = {
            'name': user_info['name']['display_name'],
            'email': user_info['email'],
            'account_id': user_info['account_id'],
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    except Exception as error:
        return HTMLResponse(f'<h1>{error}</h1>', status_code=500)

    # Redirect to client URL after successful authentication
    return RedirectResponse(CLIENT_URL)

@app.get('/logout')
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/', status_code=302)

@app.get('/profile')
async def profile(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return {'name': user['name'], 'email': user['email'], 'account_id': user['account_id']}

# === Protected Routes ===

def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return user

# === Media Management Routes ===

@app.post("/upload")
async def upload_images(
    request: Request,
    files: List[UploadFile] = File(...),
    tags: str = Form(...)
):
    user = get_current_user(request)
    uploaded_files: List[dict] = []
    for file in files:
        try:
            file_type: str = validate_image(file)
        except HTTPException as e:
            return e.detail

        file_id: str = str(uuid.uuid4())
        file_data: dict = {
            "id": file_id,
            "name": file.filename,
            "type": file_type,
            "tags": tags.split(","),
            "owner": user['account_id'],
        }
        data["files"].append(file_data)
<<<<<<< HEAD
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
async def search_files(q: str = None):
  query = q
  print('query:', query)
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
        dict(url=x.url, thumbnail_url=x.thumbnail_url, title=x.title, caption=x.caption, tags=x.tags.split(','), season=x.season, uuid=x.uuid)
        for x in results
      ]
    else:
      results = []
    return {"results": results}
  else:
    return {"results": []}
=======
        uploaded_files.append(file_data)

    return {"message": "Images uploaded successfully", "uploaded_files": uploaded_files}

@app.get("/search")
async def search_files(request: Request, query: str = None):
    user = get_current_user(request)
    user_files = [file for file in data["files"] if file["owner"] == user['account_id']]
    if query:
        result = [file for file in user_files if query.lower() in file["name"].lower()]
    else:
        result = user_files
    return {"results": result}
>>>>>>> 6e41c24 (stash)

@app.get("/tag/{file_id}")
async def get_tags(request: Request, file_id: str):
    user = get_current_user(request)
    file = next((f for f in data["files"] if f["id"] == file_id and f["owner"] == user['account_id']), None)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    tags = file.get("tags", [])
    return {"file_id": file_id, "tags": tags}

@app.put("/tag/{file_id}")
async def update_tags(request: Request, file_id: str, tags: List[str] = Form(...)):
    user = get_current_user(request)
    file = next((f for f in data["files"] if f["id"] == file_id and f["owner"] == user['account_id']), None)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    file["tags"] = tags
    return {"message": "Tags updated successfully", "file_id": file_id, "tags": tags}

# === Main Entry Point ===

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
  thumbnail_url = image_processor.resize_and_encode_image(file_path)

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
    thumbnail_url=thumbnail_url,
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
    uvicorn.run('main:app', host='localhost', port=8080, reload=True)
