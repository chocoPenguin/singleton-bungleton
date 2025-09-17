import os
from fastapi import UploadFile
from datetime import datetime

UPLOAD_DIR = "uploads"

# init upload path
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_file(file: UploadFile, group_id: int) -> str:
    """
    Saves the uploaded file to a local directory and returns the path.
    The filename is made unique by appending the group ID and timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"group{group_id}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path

def delete_file(file_path: str) -> bool:
    """
    file deletion (success: True, failure: False)
    """
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        return False