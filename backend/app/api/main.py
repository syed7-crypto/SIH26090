import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from fastapi.middleware.cors import CORSMiddleware

=======
from app.api.pricing import router as pricing_router
>>>>>>> origin/main
from app.api.routes.photos import router as photos_router
from app.api.routes.voice import router as voice_router

app = FastAPI(title="SIH26090 Artisan Commerce API")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.getenv("APP_ENV", "development").lower() == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:54874",
            "http://127.0.0.1:54874",
        ],
        allow_credentials=False,
        allow_methods=["POST", "OPTIONS"],
        allow_headers=["content-type"],
    )

app.include_router(photos_router)
app.include_router(voice_router)
app.include_router(pricing_router)