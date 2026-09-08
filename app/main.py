"""Application entry point for the current backend API."""

from fastapi import FastAPI

from app.api.pricing import router as pricing_router

app = FastAPI(title="SIH26090 API")
app.include_router(pricing_router)
