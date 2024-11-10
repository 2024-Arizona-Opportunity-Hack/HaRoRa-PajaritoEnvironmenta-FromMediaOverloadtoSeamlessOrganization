import imghdr
import json
import openai
import os
import requests
import threading
import time
import uuid
from datetime import datetime, timedelta
from queue import Queue
from typing import List
from urllib.parse import urlencode

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

import data_models
import db
import process as image_processor
import search as search_expander  # expands query into additional filters
import structured_llm_output

app = FastAPI(root_path="/api/v1")
file_queue = Queue()
job_queue = Queue()
BATCH_WINDOW_TIME_SECS = int(os.environ.get("BATCH_WINDOW_TIME_SECS", 4 * 3600))


app.add_middleware(SessionMiddleware, secret_key=os.environ["FASTAPI_SESSION_SECRET_KEY"])
# Allow Cross-Origin Resource Sharing (CORS)
origins = [
    "http://localhost",
    "http://localhost:5173",  # example frontend
    "http://peec.harora.lol"  # replace with your frontend domain
    "https://peec.harora.lol",  # replace with your frontend domain
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allows all headers
)

# ===
# AUTH
# ===

# DROPBOX Setup
AUTH_URI = "https://www.dropbox.com/oauth2/authorize"
TOKEN_URI = "https://api.dropboxapi.com/oauth2/token"
CLIENT_URL = os.environ["WEBPAGE_URL"]


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_dropbox_callback")
    # redirect_uri = "https://peec.harora.lol/api/auth/dropbox/callback"
    auth_params = {
        "client_id": os.environ["DROPBOX_CLIENT_ID"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "token_access_type": "offline",
    }
    auth_url = f"{AUTH_URI}?{urlencode(auth_params)}"
    return {"auth_url": auth_url}


@app.get("/auth/dropbox/callback")
async def auth_dropbox_callback(request: Request):
    auth_code = request.query_params["code"]
    redirect_uri = request.url_for("auth_dropbox_callback")
    # redirect_uri = "https://peec.harora.lol/api/auth/dropbox/callback"
    try:
        token_data = {
            "code": auth_code,
            "grant_type": "authorization_code",
            "client_id": os.environ["DROPBOX_CLIENT_ID"],
            "client_secret": os.environ["DROPBOX_CLIENT_SECRET"],
            "redirect_uri": redirect_uri,
        }
        token_response = requests.post(TOKEN_URI, data=token_data)
        token_response_data = token_response.json()

        access_token = token_response_data["access_token"]
        print("Access Token:", access_token)
        refresh_token = token_response_data.get("refresh_token")

        # Fetch user information
        user_info_response = requests.post(
            "https://api.dropboxapi.com/2/users/get_current_account",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_info_response.json()
        print(user_info)

        request.session["user"] = {
            "name": user_info["name"]["display_name"],
            "email": user_info["email"],
            "account_id": user_info["account_id"],
            "access_token": access_token,
        }
    except Exception as error:
        return HTMLResponse(f"<h1>{error}</h1>")
    return RedirectResponse(CLIENT_URL + "/upload")


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=302)


@app.get("/profile")
async def profile(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"name": user["name"], "email": user["email"], "account_id": user["account_id"]}


# ===
# Upload Endpoint
# ===
# Helper function to validate image file types
def validate_image(file: UploadFile):
    valid_image_formats = {"jpeg", "png", "gif", "bmp", "jpg"}
    # Check the file type using the imghdr module
    file_type = imghdr.what(file.file)
    print("File type:", file_type)
    if file_type not in valid_image_formats:
        raise HTTPException(status_code=400, detail="Invalid image format")
    return file_type


@app.post("/upload")
async def upload_images(request: Request, files: List[UploadFile] = File(...), tags: str | None = Form(...)) -> dict:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token = user["access_token"]
    account_id = user["account_id"]
    uploaded_files: List[dict] = []
    for file in files:
        file_type: str = validate_image(file)
        file_id: str = str(uuid.uuid4())
        uploaded_files.append({"file_id": file_id, "name": file.filename, "type": file_type, "tags": tags})
        # store the img in /tmp dir
        file_location = f"/tmp/{file_id}.{file_type}"
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
        file_queue.put(
            (file_location, [x.strip() for x in tags.split(",") if x.strip()], access_token, account_id, datetime.now())
        )
    return {"uploaded_files": uploaded_files}


# ===
# Search Endpoint
# ===
# Geocoding function
def get_coordinates(location):
    api_url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    headers = {"User-Agent": "PEECMediaManageMent/1.0 (rohanavad007@gmail.com)"}
    response = requests.get(api_url, headers=headers)
    data = response.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None


@app.get("/search")
async def search_files(q: str = None):
    query = q
    print("query:", query)
    if query:
        search_args = search_expander.get_search_args(query)

        # geo args
        if search_args.location is not None:
            coords = get_coordinates(search_args.location)
            distance_radius = 25_000  # 25km
        else:
            coords = None
            distance_radius = None

        query_embedding = image_processor.get_text_embedding(query)
        results = db.get_search_query_result(
            query,
            query_embedding,
            search_args.season,
            ",".join(search_args.tags),
            coords,
            distance_radius,
            search_args.date_from,
            search_args.date_to,
            match_count=50,
        )
        if results is not None:
            results = [
                dict(
                    url=x.url,
                    thumbnail_url=x.thumbnail_url,
                    title=x.title,
                    caption=x.caption,
                    tags=x.tags.split(","),
                    season=x.season,
                    uuid=x.uuid,
                )
                for x in results
            ]
        else:
            results = []
        return {"results": results}
    else:
        return {"results": []}


# ===
# Tags Endpoint
# ===


@app.put("/tag/{file_id}")
async def update_tags(file_id: str, tags: List[str]):
    db.update_tags(file_id, ",".join(tags))
    return {"message": "Tags updated successfully", "file_id": file_id, "tags": tags}


# ===
# Submit Batch Job to OAI
# ===
open("dlq", "w").close()


def file_processor():
    files_list = []
    while True:
        if not file_queue.empty():
            file_details = file_queue.get()
            files_list.append(file_details)
        else:
            time.sleep(60)
        if not len(files_list):
            continue
        if len(files_list) > 50 or (datetime.now() - files_list[0][-1] > timedelta(seconds=BATCH_WINDOW_TIME_SECS)):
            try:
                res = image_processor.process_batch(files_list)
                job_queue.put(res)
                print(f"Submitted job with id: {res[0]} to OpenAI")
            except Exception as e:
                print(e)
                with open("dlq", "a") as f:
                    f.write("\n".join([str(x) for x in files_list]) + "\n")
            finally:
                files_list = []


# ===
# Image Processing
# ===
def upload_to_dropbox(access_token, file_path, dropbox_path):
    url = "https://content.dropboxapi.com/2/files/ad"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": json.dumps(
            {"path": dropbox_path, "mode": "add", "autorename": False, "mute": False, "strict_conflict": False}
        ),
        "Content-Type": "application/octet-stream",
    }
    # Open the local file in binary mode to send it in the request
    with open(file_path, "rb") as file:
        response = requests.post(url, headers=headers, data=file)
    return response.json() if response.status_code == 200 else {"error": response.text}


def process_file(
    file_path: str, tags_list: list[str], access_token: str, img_details: dict[str, str | list[str]], account_id: str
):
    dropbox_destination_path = "/images/" + os.path.basename(file_path)
    response = upload_to_dropbox(access_token, file_path, dropbox_destination_path)
    url = f"https://www.dropbox.com/home/Apps/PEEC Media Management/images?preview={os.path.basename(file_path)}"
    thumbnail_url = image_processor.get_thumbnail(file_path)

    print("Getting title, caption, and tags ...")
    while True:
        title = img_details["title"]
        caption = img_details["image_description"]
        tags = ",".join(tags_list + img_details["tags"])
        break

    print("Getting image embeddings ...")
    while True:
        embedding_vector = image_processor.get_image_embedding(file_path)
        if embedding_vector is None:
            print("get image embedding returned None")
            continue
        break

    # extract_image_metadata
    print("Extracting metadata from image ...")
    img_metadata = image_processor.extract_image_metadata(file_path)
    coords = None
    capture_time_str = None
    season = None
    if img_metadata:
        lat = img_metadata.get("latitude", None)
        long = img_metadata.get("longitude", None)
        if lat is not None and long is not None:
            coords = [lat, long]

        capture_time = img_metadata["capture_date"]
        if capture_time is not None:
            capture_time = datetime.strptime(capture_time, "%Y:%m:%d %H:%M:%S")
            capture_time_str = capture_time.strftime("%d/%m/%Y")
            # based on month get season as either summer, fall, winter, spring
            month = capture_time.month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "fall"
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
        user_id=account_id,
    )
    print(f"Processed file: {file_path}")


# process
def compute_embeddings_and_metadata_and_push_to_db(
    batch_id, input_file_id, batch_jsonl_fp, batch_metadata_fp, batch_object
):
    with open(batch_metadata_fp, "r") as f:
        batch_metadata = json.load(f)

    print("\nbatch processing results:")
    client = openai.OpenAI()
    output_file_response = client.files.content(batch_object.output_file_id)
    json_data = output_file_response.content.decode("utf-8")
    for line in json_data.splitlines():
        json_record = json.loads(line)
        response = (
            json_record.get("response", {}).get("body", {}).get("choices", [])[0].get("message", {}).get("content")
        )
        img_details = structured_llm_output.parse_llm_response(image_processor.ImageData, response)
        if img_details is None:
            print("get_image_captioning returned None")
            continue
        image_path = json_record.get("custom_id")
        process_file(
            image_path,
            batch_metadata[image_path]["tags"],
            batch_metadata[image_path]["access_token"],
            img_details.model_dump(),
            batch_metadata[image_path]["account_id"],
        )
        try:
            os.remove(image_path)
            print(f"removed file: {image_path} sucessfully")
        except Exception as e:
            print("file removal unsuccessful. got error:", e)


def job_processor():
    client = openai.OpenAI()
    while True:
        if not job_queue.empty():
            batch_id, input_file_id, batch_jsonl_fp, batch_metadata_fp = job_queue.get()
            batch_object = client.batches.retrieve(batch_id)
            if batch_object.status in ["validating", "in_progress", "finalizing"]:
                print(f"Batch Object status:", batch_object.status)
                time.sleep(60)
                job_queue.put((batch_id, input_file_id, batch_jsonl_fp, batch_metadata_fp))
            elif batch_object.status == "completed":
                print("Caption and Tag Generation (batch job) complete")
                compute_embeddings_and_metadata_and_push_to_db(
                    batch_id, input_file_id, batch_jsonl_fp, batch_metadata_fp, batch_object
                )
                # clean up
                try:
                    client.files.delete(input_file_id)
                    client.files.delete(batch_object.output_file_id)
                    os.remove(batch_jsonl_fp)
                    os.remove(batch_metadata_fp)
                    print("Clean up and everything done for batch:", batch_id)
                except Exception as e:
                    print("Clean up messed up with err:", e)
            else:
                print(f"batch job failed with status: {batch_object.status}")

        else:
            time.sleep(5)


# Start a background thread for processing files
threading.Thread(target=file_processor, daemon=True).start()
threading.Thread(target=job_processor, daemon=True).start()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="localhost", port=8080, reload=True)

    """
    # test if file_processor and job_processor threads work appropriately, by adding to images to the first queue
    # image files: ../../image.jpg, ../screenshot.png
    file_queue.put(("../../image.png", ["tag1", "tag2"], "access_token", datetime.now()))
    file_queue.put(("../screenshot.png", ["tag3", "tag4"], "access_token", datetime.now()))

    input('Do not press Enter, else program will stop')
    """
