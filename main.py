from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import shutil

app = FastAPI()

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload(
    image: UploadFile = File(...),
    video: UploadFile = File(...),
    description: str = Form(...)
):
    def save_file(file: UploadFile):
        base, ext = os.path.splitext(file.filename)
        timestamp = int(time.time() * 1000)
        filename = f"{base}_{timestamp}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return f"/tmp/{filename}"

    # image_url = save_file(image)
    # video_url = save_file(video)

    print("-------------------------------")
    # print(image_url)
    # print(video_url)
    print(description)

    return JSONResponse(
        content={
            "message": "Upload successful",
            "image": image_url,
            "video": video_url,
            "description": description,
        }
    )
