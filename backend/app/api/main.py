from fastapi import FastAPI

from app.api.routes.photos import router as photos_router

app = FastAPI(title="SIH26090 Artisan Commerce API")
app.include_router(photos_router)
