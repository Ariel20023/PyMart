import os
import time
from uuid import uuid4
import json

from elasticsearch import Elasticsearch

from app.services.storage_client import upload_local_image_to_storage


ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL","http://elasticsearch:9200"
)

PRODUCTS_INDEX = os.getenv("PRODUCTS_INDEX","products")

es = Elasticsearch(ELASTICSEARCH_URL)


def wait_for_elasticsearch():#ממתין עד שהאלסטיק עולה 
    for attempt in range(60):#מנסה כמות פעמים להעלות
        try:
            if es.ping():#האם האלסטיק חי 
                print("Elasticsearch connected")
                return#יוצא מהפונקציה

        except Exception as e:
            print(f"Waiting {e}")

        time.sleep(2)#ממתין לפני ניסיון נוסף

    raise RuntimeError("Elasticsearch is not ready")#מקריס את האפליקציה 

#לא צריך את הפונקציה הזו זה רק לבטחון נלקח מהאינטרנט
def safe_elasticsearch_call(func, *args, **kwargs):#אם אלסטיק לא זמין מנסה שוב ולא ישר מקריסמביא  פונקציה עןם פרמטרים
    for attempt in range(5):#מנסה עד 5 פעמים
        try:
            return func(*args, **kwargs)

        except Exception as e:
            print(f"Elasticsearch call failed, retrying... {e}")
            wait_for_elasticsearch()
            time.sleep(2)

    raise RuntimeError("Elasticsearch call failed after retries")


def create_products_index():
    wait_for_elasticsearch()
#בודק אם יש אינדקס לא נצרך 
    index_exists = safe_elasticsearch_call(
        es.indices.exists,
        index=PRODUCTS_INDEX
    )

    if index_exists:
        return
#נתיב ל2 תקיות למעלה כי רוצים להגיע להגדרות mapping 
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
#יוצר נטיב לקובץ mapping 
    mapping_file = os.path.join(
        base_dir,
        "config",
        "mapping.json"
    )
#טוען את ההגדרות
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
#יוצר אינדקס בצורה בטוחה לא נצרך ולא ברור עד הסוף זה היה כי היה משהו תקוע
    safe_elasticsearch_call(
        es.indices.create,
        index=PRODUCTS_INDEX,
        mappings=mapping
    )


def seed_products():
    wait_for_elasticsearch()
#הופך קריאות של אלסטיק ליוצר אמינות ויציבות 
    count = safe_elasticsearch_call(
        es.count,
        index=PRODUCTS_INDEX
    )

    if count["count"] != 0:
        return

    products = [
        {
            "name": "Piano",
            "description": "Professional piano",
            "price": 120000,
            "category": "Instruments",
            "stock_count": 3,
            "image_path": "app/images/piano.jpg",
        },
        {
            "name": "Guitar",
            "description": "Classic acoustic guitar",
            "price": 3500,
            "category": "Instruments",
            "stock_count": 12,
            "image_path": "app/images/guitar.jpg",
        },
        {
            "name": "Drums",
            "description": "Full professional drum set",
            "price": 8500,
            "category": "Instruments",
            "stock_count": 5,
            "image_path": "app/images/drums.jpg",
        },
        {
            "name": "Organ",
            "description": "Electronic keyboard organ",
            "price": 6200,
            "category": "Instruments",
            "stock_count": 7,
            "image_path": "app/images/organ.jpg",
        },
        {
            "name": "Violin",
            "description": "Classic wooden violin",
            "price": 4800,
            "category": "Instruments",
            "stock_count": 6,
            "image_path": "app/images/violin.jpg",
        }
    ]

    for product in products:
        product_id = str(uuid4())
        image_path = product.pop("image_path")

        try:
            product["image_url"] = upload_local_image_to_storage(product_id=product_id,
                image_path=image_path,
            )

        except Exception as e:
            print(f"Image upload failed for {product['name']}: {e}")
            product["image_url"] = None

        safe_elasticsearch_call(
            es.index,
            index=PRODUCTS_INDEX,
            id=product_id,
            document=product,
            refresh=True,
        )