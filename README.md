# PyMart Microservices

This version splits the original M1 service into:

- `auth_service` - users, login, register, token validation, admin validation
- `catalog_service` - products and Elasticsearch
- `storage_service` - product images and MinIO
- `frontend` - Streamlit UI

## Run

```bash
docker compose up --build
```

Then open:

- Storefront: http://localhost:8501
- Catalog API: http://localhost:8000/docs
- Auth API: http://localhost:8001/docs
- Storage API: http://localhost:8002/docs
- MinIO Console: http://localhost:9001

Default admin:

- email: `admin@pymart.com`
- password: `admin123`

## Images folder

Put seed images here if you want the initial products to have images:

```text
catalog_service/app/images/
```

Expected names:

```text
piano.jpg
guitar.jpg
drums.jpg
organ.jpg
violin.jpg
```

If the images are missing, the project still runs. The seeded products will have `image_url = null`.
