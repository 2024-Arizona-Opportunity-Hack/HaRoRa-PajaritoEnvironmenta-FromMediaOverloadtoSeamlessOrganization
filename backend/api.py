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
        # create folder
        create_dropbox_folder(access_token, "/Apps/PEEC Media Management")
        template_id = create_dropbox_template(access_token)
        # check if user exists in DB
        user = db.read_user(user_info["account_id"])
        # if no: create one and add to db
        if user is None:
            db.create_user(
                data_models.User(
                    user_info["account_id"],
                    user_info["name"]["display_name"],
                    user_info["email"],
                    access_token,
                    refresh_token,
                    template_id,
                )
            )
        # if exists: update access_token and refresh_token
        else:
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.template_id = template_id
            db.update_user(user.user_id, user)
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
        file_location = os.path.join("/tmp", account_id, f"{file_id}.{file_type}")  # Download to the folder
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
        db.create_file_queue(data_models.FileQueue(file_location, tags, access_token, account_id))
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
async def search_files(request: Request, q: str = None):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

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
            user["account_id"],
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
# Utils
# ===
def create_dropbox_folder(access_token, folder_path):
    url = "https://api.dropboxapi.com/2/files/create_folder_v2"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"path": folder_path, "autorename": False}
    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return "Folder created successfully."
        elif response.status_code == 409:
            return "Folder already exists. No action taken."
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error creating folder: {str(e)}")


def create_dropbox_template(access_token):
    # API endpoints
    add_template_url = "https://api.dropboxapi.com/2/file_properties/templates/add_for_user"
    list_templates_url = "https://api.dropboxapi.com/2/file_properties/templates/list_for_user"

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # Template data
    template_data = {
        "description": "These properties describe the images in the folder.",
        "fields": [
            {"description": "This is the caption of the image.", "name": "Caption", "type": "string"},
            {"description": "This is the title of the image.", "name": "Title", "type": "string"},
        ],
        "name": "Image Info",
    }

    # Check if template already exists
    response = requests.post(list_templates_url, headers=headers)
    response.raise_for_status()
    existing_templates = response.json().get("template_ids", [])

    for template_id in existing_templates:
        template_info_url = f"https://api.dropboxapi.com/2/file_properties/templates/get_for_user"
        template_info_data = {"template_id": template_id}
        template_info_response = requests.post(template_info_url, headers=headers, json=template_info_data)
        template_info_response.raise_for_status()
        template_info = template_info_response.json()

        if (
            template_info["name"] == template_data["name"]
            and len(template_info["fields"]) == len(template_data["fields"])
            and all(field["name"] in [f["name"] for f in template_data["fields"]] for field in template_info["fields"])
        ):
            return template_id

    # If template doesn't exist, create it
    response = requests.post(add_template_url, headers=headers, json=template_data)
    response.raise_for_status()
    return response.json()["template_id"]


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
def file_processor():
    while True:
        unbatched_files = db.get_unbatched_files()
        print("Unbatched_files:", unbatched_files)
        if unbatched_files is not None:
            if len(unbatched_files) >= 50 or (
                datetime.utcnow() - unbatched_files[0].created_at > timedelta(seconds=BATCH_WINDOW_TIME_SECS)
            ):
                try:
                    files_list = [
                        (
                            x.tmp_file_loc,
                            [y.strip() for y in x.tag_list.split(",") if y.strip()],
                            x.access_token,
                            x.user_id,
                        )
                        for x in unbatched_files
                    ]
                    res = image_processor.process_batch(files_list)
                    print("process_batch_outuput:", res)
                    db.create_batch_queue(data_models.BatchQueue(*res))
                    print(f"Submitted job with id: {res[0]} to OpenAI")

                    for x in unbatched_files:
                        x.batch_id = res[0]
                        db.update_file_queue(x.tmp_file_loc, x)
                except Exception as e:
                    print(e)
                    with open("dlq", "a") as f:
                        f.write("\n".join([str(x) for x in files_list]) + "\n")
                finally:
                    files_list = []

        time.sleep(60)


# ===
# Image Processing
# ===
def upload_to_dropbox(access_token, file_path, dropbox_path):
    url = "https://content.dropboxapi.com/2/files/upload"
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


def add_tag_to_dropbox_file(access_token: str, path: str, tag_text: str) -> None:
    url: str = "https://api.dropboxapi.com/2/files/tags/add"
    headers: dict = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data: dict = {"path": path, "tag_text": tag_text}

    response: requests.Response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Tag added successfully.")
    else:
        print(f"Error occurred: {response.status_code}, {response.text}")


def process_file(
    file_path: str, tags_list: list[str], access_token: str, img_details: dict[str, str | list[str]], account_id: str
):
    dropbox_destination_path = "/Apps/PEEC Media Management/images/" + os.path.basename(file_path)
    response = upload_to_dropbox(access_token, file_path, dropbox_destination_path)
    print(response)
    url = f"https://www.dropbox.com/home/Apps/PEEC Media Management/images?preview={os.path.basename(file_path)}"
    thumbnail_url = image_processor.get_thumbnail(file_path)

    print("Getting title, caption, and tags ...")
    title = img_details["title"]
    caption = img_details["image_description"]
    final_tags_list = tags_list + img_details["tags"]
    tags = ",".join(final_tags_list)
    # push tags to dropbox
    for t in final_tags_list:
        add_tag_to_dropbox_file(access_token, dropbox_destination_path, t.replace(" ", "_"))
    # get template id for curr user
    user = db.read_user(account_id)
    template_id = user.template_id
    # push title and caption property for that image to dropbox
    payload_data = {
        "path": dropbox_destination_path,
        "property_groups": [
            {
                "fields": [{"name": "Title", "value": title}, {"name": "Caption", "value": caption}],
                "template_id": template_id,
            }
        ],
    }
    res = requests.post(
        "https://api.dropboxapi.com/2/file_properties/properties/add",
        json=payload_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if res.status_code != 200 and res.status_code != 409:
        res.raise_for_status()

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
    db.mark_file_as_saved(file_path)
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
        if not db.is_file_saved_to_db(image_path):
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
        running_batch_jobs: list[data_models.BatchQueue] = db.get_running_batch_jobs()
        if running_batch_jobs is not None:
            for batch_item in running_batch_jobs:
                batch_object = client.batches.retrieve(batch_item.batch_id)
                batch_item.status = batch_object.status
                if batch_object.status in ["validating", "in_progress", "finalizing"]:
                    print(f"Batch Object status:", batch_object.status)
                elif batch_object.status == "completed":
                    print("Caption and Tag Generation (batch job) complete")
                    batch_item.output_file_id = batch_object.output_file_id
                    compute_embeddings_and_metadata_and_push_to_db(
                        batch_item.batch_id,
                        batch_item.input_file_id,
                        batch_item.batch_jsonl_filepath,
                        batch_item.batch_metadata_filepath,
                        batch_object,
                    )
                    batch_item.are_all_files_updated_in_db = True
                else:
                    print(f"batch job failed with status: {batch_object.status}")

                db.update_batch_queue(batch_item.batch_id, batch_item)
        else:
            time.sleep(60)


def garbage_collector():
    # clean up files from disk and oai storage and everywhere else it needs to be cleaned from
    client = openai.OpenAI()
    while True:
        # remove files
        uncleaned_files = db.get_uncleaned_files()
        if uncleaned_files is not None:
            for file_item in uncleaned_files:
                try:
                    os.remove(file_item.tmp_file_loc)
                    file_item.is_cleaned_from_disk = True
                    db.update_file_queue(file_item.tmp_file_loc, file_item)
                except FileNotFoundError:
                    file_item.is_cleaned_from_disk = True
                    db.update_file_queue(file_item.tmp_file_loc, file_item)
                except Exception as e:
                    print("File cleaning broke because of error:", e)

        # remove batch files
        completed_batches = db.get_completed_jobs_but_not_cleaned()
        if completed_batches is not None:
            for batch_item in completed_batches:
                # check if all files from that batch are done, if yes continue else skip next steps
                still_in_process = False
                if not batch_item.are_all_files_updated_in_db:
                    batch_files = db.get_files_by_batch_id(batch_item.batch_id)
                    if batch_files is not None:
                        for f in batch_files:
                            if not f.is_saved_to_db:
                                still_in_process = True
                                break
                if still_in_process:
                    continue
                try:
                    if not batch_item.are_files_deleted_from_oai_storage:
                        client.files.delete(batch_item.input_file_id)
                        client.files.delete(batch_item.output_file_id)
                        batch_item.are_files_deleted_from_oai_storage = True
                    if not batch_item.is_cleaned_from_disk:
                        os.remove(batch_item.batch_jsonl_filepath)
                        os.remove(batch_item.batch_metadata_filepath)
                        batch_item.is_cleaned_from_disk = True
                    print("Clean up and everything done for batch:", batch_item.batch_id)
                except Exception as e:
                    print("Clean up messed up with err:", e)
                finally:
                    db.update_batch_queue(batch_item.batch_id, batch_item)

        time.sleep(24 * 3600)  # run once a day


# ===
# Poller
# ===
def list_dropbox_folder(access_token: str, filepath: str, cursor: str | None = None) -> dict:
    headers: dict = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    if cursor is None:
        url = "https://api.dropboxapi.com/2/files/list_folder"
        data: dict = {
            "include_deleted": False,
            "include_has_explicit_shared_members": True,
            "include_media_info": True,
            "include_mounted_folders": True,
            "include_non_downloadable_files": False,
            "path": filepath,
            "recursive": True,
        }
    else:
        url = "https://api.dropboxapi.com/2/files/list_folder/continue"
        data = {"cursor": cursor}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def pol_from_dropbox():
    while True:
        # get all users
        users_list = db.get_all_users()
        for user in users_list:
            print(f"Looking into user: {user.user_name}")
            ROOT_PATH = "/Apps/PEEC Media Management/images"
            while True:
                res = list_dropbox_folder(user.access_token, ROOT_PATH, user.cursor)
                user.cursor = res["cursor"]
                for ent in res["entries"]:
                    handle_dropbox_files(ent, user.access_token, user.user_id)
                if not res["has_more"]:
                    break
            db.update_user(user.user_id, user)

        time.sleep(24 * 3600)  # once in a day


def handle_dropbox_files(ent, access_token, user_id):
    print(f'Handling {ent["name"]} file')
    if ent[".tag"] != "file":
        return None
    if not (ent["name"].lower().endswith((".jpg", ".jpeg", ".png"))):
        return None
    # check if already processed in DB
    url = f"https://www.dropbox.com/home{os.path.dirname(ent['path_display'])}?preview={ent['name']}"
    if db.check_image_exists(url, user_id):
        return None
    # check if in queue
    file_name = ent["name"]
    file_path = os.path.join("/tmp", user_id, file_name)  # Download to the folder
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if db.read_file_queue(file_path) is not None:
        return None
    # Download the file
    download_url = "https://content.dropboxapi.com/2/files/download"
    download_headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": f"{{\"path\": \"{ent['path_display']}\"}}",
    }
    file_response = requests.post(download_url, headers=download_headers)
    with open(file_path, "wb") as f:
        f.write(file_response.content)
    print(f" Downloaded: {file_name} to {file_path}")
    db.create_file_queue(data_models.FileQueue(file_path, "", access_token, user_id))


# Start a background thread for processing files
threading.Thread(target=file_processor, daemon=True).start()
threading.Thread(target=job_processor, daemon=True).start()
threading.Thread(target=garbage_collector, daemon=True).start()
threading.Thread(target=pol_from_dropbox, daemon=True).start()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="localhost", port=8080, reload=True)
