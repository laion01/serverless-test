import base64
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv


# Load from .env file in current directory
load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

def generate_image(prompt="a boot with an eye", n=1):

    response = client.images.generate(
        model="gpt-image-1",
        prompt=f"{prompt}, centered, full view, isolated on white background, no cropping, product render style",
        # prompt=f"wbgmsst, {prompt}, 3D isometric on white background, no cropping, product render style",
        quality="low",
        n=n,
        size="1024x1024",
    )

    images = []
    for i, item in enumerate(response.data):
        images.append(item.b64_json)
        
    return images