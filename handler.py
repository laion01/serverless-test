import requests

def handler(event):
    # Assume these are base64-encoded or raw data from frontend
    image_url = event["input"]["image_url"]
    video_url = event["input"]["video_url"]
    description = event["input"]["description"]

    # Download files locally (or assume already passed as multipart in real deploy)
    image_data = requests.get(image_url).content
    video_data = requests.get(video_url).content

    files = {
        "image": ("image.png", image_data, "image/png"),
        "video": ("video.mp4", video_data, "video/mp4")
    }

    data = {"description": description}

    response = requests.post("http://localhost:8000/upload", files=files, data=data)

    return response.json()
