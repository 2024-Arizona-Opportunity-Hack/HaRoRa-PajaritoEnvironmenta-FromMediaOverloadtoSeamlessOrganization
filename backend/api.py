from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
import imghdr

app = FastAPI()

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

# POST /upload (Batch upload for images)
@app.post("/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        # Validate the file is an image
        try:
            file_type = validate_image(file)
        except HTTPException as e:
            return e.detail

        # Create a unique file ID and save the image details
        file_id = str(uuid.uuid4())
        file_data = {"id": file_id, "name": file.filename, "type": file_type}
        data["files"].append(file_data)
        uploaded_files.append({"file_id": file_id, "name": file.filename, "type": file_type})
    
    return {"message": "Images uploaded successfully", "uploaded_files": uploaded_files}

# GET /search
@app.get("/search")
async def search_files(query: str = None):
    if query:
        result = [file for file in data["files"] if query.lower() in file["name"].lower()]
    else:
        result = data["files"]
    return {"result": result}

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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('api:app', host='localhost', port=8080, reload=True)

