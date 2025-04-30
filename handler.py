"""RunPod serverless handler that saves an image and video file temporarily, and uses a prompt."""

import runpod
import os
import uuid
import base64

def save_base64_file(base64_string, extension):
    filename = f"/tmp/{uuid.uuid4()}.{extension}"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(base64_string))
    return filename

def handler(job):
    job_input = job["input"]

    image_b64 = job_input.get("image_base64")
    video_b64 = job_input.get("video_base64")
    prompt = job_input.get("prompt", "")
    image_ext = job_input.get("image_ext", "png")
    video_ext = job_input.get("video_ext", "mp4")

    if not image_b64 or not video_b64:
        return {"error": "Both image_base64 and video_base64 are required."}

    try:
        # Save image and video to /tmp
        image_path = save_base64_file(image_b64, image_ext)
        video_path = save_base64_file(video_b64, video_ext)

        # You can now process the files and use the prompt
        # Example dummy response
        result = {
            "image_path": image_path,
            "video_path": video_path,
            "prompt_used": prompt
        }

        # Cleanup after processing
        os.remove(image_path)
        os.remove(video_path)

        return result

    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
