import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.pricing import router as pricing_router
from app.api.routes.photos import router as photos_router
from app.api.routes.voice import router as voice_router

app = FastAPI(title="SIH26090 Artisan Commerce API")

if os.getenv("APP_ENV", "development").lower() == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(photos_router)
app.include_router(voice_router)
app.include_router(pricing_router)