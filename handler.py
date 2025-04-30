import runpod
import os
import uuid
import base64

def save_base64_file(base64_string, extension):
    filename = f"/tmp/{uuid.uuid4()}.{extension}"
    try:
        with open(filename, "wb") as f:
            f.write(base64.b64decode(base64_string))
        return filename
    except Exception as e:
        raise Exception(f"Failed to save file: {e}")

def handler(job):
    job_input = job["input"]

    image_b64 = job_input.get("image_base64")
    video_b64 = job_input.get("video_base64")
    prompt = job_input.get("prompt", "")
    image_ext = job_input.get("image_ext", "png")
    video_ext = job_input.get("video_ext", "mp4")

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

        result = {
            "image_path": image_path,
            "video_path": video_path,
            "prompt_used": prompt
        }

        return result

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
