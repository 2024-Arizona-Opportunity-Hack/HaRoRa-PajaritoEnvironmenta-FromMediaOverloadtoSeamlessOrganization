import requests
import os

def download_file_from_dropbox(access_token, cursor=None, download_folder="/tmp"):
    # Create the folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 1: If no cursor, get the first file
    if cursor is None:
        url = "https://api.dropboxapi.com/2/files/list_folder"
        data = {
            "path": "",
            "recursive": False,
            "include_deleted": False,
            "include_has_explicit_shared_members": False,
            "include_mounted_folders": True,
            "include_non_downloadable_files": True
        }
    else:
        # Step 2: Use the cursor to get the next file(s)
        url = "https://api.dropboxapi.com/2/files/list_folder/continue"
        data = {
            "cursor": cursor
        }
    
    # Make the request
    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()

    # Step 3: Check if there are any files
    if 'entries' not in response_json or len(response_json['entries']) == 0:
        print("No files found.")
        return

    # Step 4: Download the first file in the list
    file = response_json['entries'][0]
    if file[".tag"] == "file" and file["name"].lower().endswith(('.jpg', '.jpeg', '.png')):
        download_url = "https://content.dropboxapi.com/2/files/download"
        download_headers = {
            "Authorization": f"Bearer {access_token}",
            "Dropbox-API-Arg": f"{{\"path\": \"{file['path_lower']}\"}}"
        }
        
        # Download the file
        file_response = requests.post(download_url, headers=download_headers)
        file_name = file["name"]
        file_path = os.path.join(download_folder, file_name)  # Download to the folder

        with open(file_path, "wb") as f:
            f.write(file_response.content)
        print(f"Downloaded: {file_name} to {download_folder}")
    
    # Step 5: Return the cursor for the next batch
    return response_json.get("cursor")

# Example usage
access_token = ""

# First time, no cursor
cursor = download_file_from_dropbox(access_token)

# Subsequent calls with a cursor
if cursor:
    cursor = download_file_from_dropbox(access_token, cursor)
