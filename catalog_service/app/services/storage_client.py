import os
import requests
from fastapi import HTTPException, UploadFile

STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://storage_service:8002")

#מקבל תמונה מהפרונט ושולח אותה ל storge service
def upload_file_to_storage(product_id: str, image: UploadFile) -> str:
    try:
        response = requests.post(
            f"{STORAGE_SERVICE_URL}/images/products/{product_id}",
            files={"image": (image.filename, image.file, image.content_type)},
            timeout=20
        )
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Storage service is not available")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Storage service error")

    return response.json()["image_url"]


def upload_local_image_to_storage(product_id: str, image_path: str) -> str | None:
    if not os.path.exists(image_path):
        return None

    file_name = os.path.basename(image_path)

    with open(image_path, "rb") as image_file:
        try:
            response = requests.post(
                f"{STORAGE_SERVICE_URL}/images/products/{product_id}",files={"image": (file_name, image_file, _get_content_type(file_name))},
                timeout=20
            )
        except requests.RequestException:
            return None

    if response.status_code != 200:
        return None

    return response.json()["image_url"]


def _get_content_type(file_name: str): #מיותר 
    extension = os.path.splitext(file_name)[1].lower()

    if extension in [".jpg", ".jpeg"]:
        return "image/jpeg"

    if extension == ".png":
        return "image/png"

    if extension == ".webp":
        return "image/webp"

    return "application/octet-stream"
