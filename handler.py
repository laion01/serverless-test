import runpod
import os
import uuid
import base64
import b2sdk.v2 as b2
from pathlib import Path
import os
from time import time
from PIL import Image
import torch
from diffusers import DiffusionPipeline
from typing import Tuple
from datetime import datetime

default_negative = os.getenv("default_negative","")

style_list = [
    {
        "name": "3D Model",
        "prompt": "{prompt}, centered, full view, isolated on white background, no cropping, product render style",
        "negative_prompt": "",
    },
]

styles = {k["name"]: (k["prompt"], k["negative_prompt"]) for k in style_list}
STYLE_NAMES = list(styles.keys())
DEFAULT_STYLE_NAME = "3D Model"

def apply_style(style_name: str, positive: str, negative: str = "") -> Tuple[str, str]:
    p, n = styles.get(style_name, styles[DEFAULT_STYLE_NAME])
    
    if not negative:
        negative = ""
    p = p.replace("{prompt}", positive)
    return p, n + negative

USE_TORCH_COMPILE = os.getenv("USE_TORCH_COMPILE", "0") == "1"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

NUM_IMAGES_PER_PROMPT = 1

if torch.cuda.is_available():
    pipe = DiffusionPipeline.from_pretrained(
        "SG161222/RealVisXL_V5.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        add_watermarker=False,
        variant="fp16"
    )
    pipe.to("cuda")
    
    if USE_TORCH_COMPILE:
        pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)

def save_image(img, output_path):
    img.save(output_path)
    return output_path

def generate_image(
    prompt: str, seed: int = 0, n = 1
):
    print("---------------- generating images. ----------------")
    prompt = prompt + ", centered, full view, 3D isolated on white background, no cropping, product render style"
    negative_prompt = "blur,stratch"
    generator = torch.Generator().manual_seed(0)

    options = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": 1024,
        "height": 1024,
        'seed': seed,
        "guidance_scale": 20,
        "num_inference_steps": 25,
        "generator": generator,
        "num_images_per_prompt": n,
        "use_resolution_binning": True,
        "output_type": "pil",
    }

    images = pipe(**options).images
    saved_files = []
    for i, item in enumerate(images):
        filename = datetime.now().strftime("/RealVisXL_%Y%m%d_%H%M%S") + f"_base_{i+1}.png"
        item.save(filename)
        saved_files.append(filename)
        print(f"Saved: {filename}")

    if n==1:
        return saved_files[0]
    return saved_files

    
# --- B2 Setup ---
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

    image_path = video_path = None
    images = generate_image(prompt)
    try:

        return {
            "prompt": prompt + "return ing",
            "imageFile": images
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
