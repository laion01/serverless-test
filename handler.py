import runpod
import os
import uuid
import base64
import b2sdk.v2 as b2
from pathlib import Path

# --- B2 Setup ---
B2_APPLICATION_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

info = b2.InMemoryAccountInfo()
b2_api = b2.B2Api(info)
b2_api.authorize_account("production", B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY)
bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)


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

    image_path = video_path = None

    try:

        return {
            "prompt": prompt,
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Safe cleanup
        for file_path in [image_path, video_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as cleanup_error:
                    print(f"Failed to delete {file_path}: {cleanup_error}")


runpod.serverless.start({"handler": handler})
