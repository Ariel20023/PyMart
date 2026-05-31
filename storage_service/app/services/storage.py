from minio import Minio
from fastapi import UploadFile
import os
import json


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


class MinioService:
    def __init__(self):
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )

    def ensure_bucket_exists(self):#בודק אם כבר קיים באקט
        if not self.client.bucket_exists(MINIO_BUCKET):
            self.client.make_bucket(MINIO_BUCKET)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{MINIO_BUCKET}/*"]
                }
            ]
        }

        self.client.set_bucket_policy(
            MINIO_BUCKET,
            json.dumps(policy)
        )

    def upload_uploaded_file(self, product_id: str, file: UploadFile):
        self.ensure_bucket_exists()

        file_extension = os.path.splitext(file.filename)[1]#סיומת הקובץ כלומר רק הסיום בלי השם
        object_name = f"products/{product_id}{file_extension}"

        self.client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type
        )

        return f"{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{object_name}"

    def upload_product_image(self, product_id: str, image_path: str):#תמונה מקובץ מקומי
        self.ensure_bucket_exists()

        file_extension = os.path.splitext(image_path)[1]
        object_name = f"products/{product_id}{file_extension}"

        self.client.fput_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            file_path=image_path,
            content_type=self._get_content_type(file_extension)
        )

        return f"{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{object_name}"

    def _get_content_type(self, file_extension: str):#מיותר אפשר למחוק
        if file_extension.lower() in [".jpg", ".jpeg"]:
            return "image/jpeg"

        if file_extension.lower() == ".png":
            return "image/png"

        if file_extension.lower() == ".webp":
            return "image/webp"

        return "application/octet-stream"