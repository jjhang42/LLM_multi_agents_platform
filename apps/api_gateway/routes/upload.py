# apps/api_gateway/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/api/tasks/{task_id}/upload")
async def upload_file(task_id: str, file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[-1]
    uid = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, uid)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return JSONResponse({"filename": uid, "path": file_path})
