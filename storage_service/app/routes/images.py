from fastapi import APIRouter, UploadFile, File

from app.services.storage import MinioService
router = APIRouter()


@router.post("/images/products/{product_id}")
def upload_product_image(product_id: str, image: UploadFile = File(...)):
    minio_service = MinioService()

    image_url = minio_service.upload_uploaded_file(
        product_id=product_id,
        file=image
    )

    return {"image_url": image_url}
#מקבל תמונה מסרוויס ומעלה ל minio