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

    image_b64 = job_input.get("image_base64")
    video_b64 = job_input.get("video_base64")
    prompt = job_input.get("prompt", "")
    image_ext = job_input.get("image_ext", "png")
    video_ext = job_input.get("video_ext", "mp4")
    user_id = job_input.get("user_id")

    if not user_id:
        return {"error": "Missing required field: user_id"}
    if not image_b64 and not video_b64:
        return {"error": "No file uploaded. Both image_base64 and video_base64 are missing."}
    elif not image_b64:
        return {"error": "No image uploaded. 'image_base64' is missing."}
    elif not video_b64:
        return {"error": "No video uploaded. 'video_base64' is missing."}

    image_path = video_path = None

    try:
        # Save image and video to /tmp
        image_path = save_base64_file(image_b64, image_ext)
        video_path = save_base64_file(video_b64, video_ext)

        # Upload to B2
        # image_b2_url = upload_to_b2(image_path, user_id, "image")
        # video_b2_url = upload_to_b2(video_path, user_id, "video")

        return {
            "user_id": B2_APPLICATION_KEY_ID,
            "prompt_used": B2_APPLICATION_KEY,
            "image_b2_url": B2_BUCKET_NAME,
            "video_b2_url": image_path,
        }

        # return {
        #     "user_id": user_id,
        #     "prompt_used": prompt,
        #     "image_b2_url": image_b2_url,
        #     "video_b2_url": video_b2_url,
        # }

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
