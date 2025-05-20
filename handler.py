import runpod
import os
import uuid
import base64
import b2sdk.v2 as b2
from pathlib import Path
from time import time
from PIL import Image
import torch
from diffusers import DiffusionPipeline
from typing import Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from openai_image import generate_image as openai_img
# from image_openai_multicheck import generate_image as openai_multi_img
from realvisxl_image import generate_image as realvis_img

# --- B2 Setup (optional, commented) ---
# B2_APPLICATION_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID")
# B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
# B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

# info = b2.InMemoryAccountInfo()
# b2_api = b2.B2Api(info)
# b2_api.authorize_account("production", B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY)
# bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)

def save_base64_file(base64_string, extension):
    filename = f"/tmp/{uuid.uuid4()}.{extension}"
    try:
        with open(filename, "wb") as f:
            f.write(base64.b64decode(base64_string))
        return filename
    except Exception as e:
        raise Exception(f"Failed to save file: {e}")

def upload_to_b2(local_path, user_id, file_type):
    file_name = f"{user_id}/media/{Path(local_path).name}"
    try:
        with open(local_path, "rb") as file:
            bucket.upload_bytes(file.read(), file_name)
        return f"b2://{B2_BUCKET_NAME}/{file_name}"
    except Exception as e:
        raise Exception(f"Failed to upload {file_type} to B2: {e}")

def handler(job):
    job_input = job["input"]
    prompt = job_input.get("prompt", "")
    rCount = job_input.get("rCount", 1)
    oCount = job_input.get("oCount", 1)

    r_images = []
    o_images = []

    try:
        with ThreadPoolExecutor() as executor:
            # Submit openai_img if requested
            o_future = executor.submit(openai_img, prompt, oCount) if oCount > 0 else None

            # Run realvis_img in main thread
            if rCount > 0:
                r_images = realvis_img(prompt, rCount)

            # Get openai_img result if applicable
            if o_future:
                o_images = o_future.result()

        return {
            "prompt": prompt + " return ing",
            "openAI_Images": o_images,
            "realVis_Images": r_images
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        print("Image generation success")

runpod.serverless.start({"handler": handler})
