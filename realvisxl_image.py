import os
from time import time
from PIL import Image
import torch
from diffusers import DiffusionPipeline
from typing import Tuple
from datetime import datetime

default_negative = os.getenv("default_negative","")
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cuda", type=int, default=0)
    return parser.parse_args()

args = get_args()

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
    pipe.to(f"cuda:{args.cuda}")
    
    if USE_TORCH_COMPILE:
        pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)

def save_image(img, output_path):
    img.save(output_path)
    return output_path

def generate_image(
    prompt: str, n = 1
):
    prompt = prompt + ", centered, full view, 3D isolated on white background, no cropping, product render style"
    negative_prompt = "blur,stratch"
    generator = torch.Generator().manual_seed(0)

    options = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": 1024,
        "height": 1024,
        'seed': 0,
        "guidance_scale": 20,
        "num_inference_steps": 25,
        "generator": generator,
        "num_images_per_prompt": n,
        "use_resolution_binning": True,
        "output_type": "pil",
    }

    images = pipe(**options).images
    base64_images = []

    for i, image in enumerate(images):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        b64_string = base64.b64encode(buffer.read()).decode("utf-8")
        base64_images.append(b64_string)
        print(f"Generated image {i+1} as base64")

    return base64_images