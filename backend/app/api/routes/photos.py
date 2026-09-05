"""Photo upload and Photo Intelligence API routes."""

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.config.settings import get_settings
from app.services.vision import MediaProcessor, VisionClient, validate_media_output

router = APIRouter(prefix="/api/v1/products", tags=["photos"])

MIN_PHOTOS = 2
MAX_PHOTOS = 5
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SUPPORTED_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "BMP": ".bmp",
    "TIFF": ".tiff",
}


async def _read_and_validate_image(upload: UploadFile) -> tuple[bytes, str]:
    """Read one upload and return its bytes and server-selected extension."""

    image_bytes = await upload.read(MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Each image must be 10 MB or smaller.",
        )

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image_format = image.format
            image.verify()
        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Each upload must be a valid supported image.",
        ) from exc

    extension = SUPPORTED_FORMATS.get(image_format or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Supported image formats are JPG, JPEG, PNG, WebP, BMP, and TIFF.",
        )
    return image_bytes, extension


@router.post("/{product_id}/photos/analyze")
async def analyze_product_photos(
    product_id: str,
    photos: list[UploadFile] = File(...),
) -> dict:
    """Store uploaded photos and run the existing Photo Intelligence service."""

    if not MIN_PHOTOS <= len(photos) <= MAX_PHOTOS:
        raise HTTPException(
            status_code=422,
            detail="Upload between 2 and 5 photos.",
        )

    validated_uploads = [await _read_and_validate_image(photo) for photo in photos]
    settings = get_settings()
    storage_root = Path(settings.storage_root).resolve()
    upload_directory = storage_root / "photo_analysis" / uuid4().hex
    upload_directory.mkdir(parents=True, exist_ok=False)

    images: list[dict[str, str]] = []
    for image_bytes, extension in validated_uploads:
        image_id = f"img-{uuid4().hex}"
        filename = f"{image_id}{extension}"
        destination = upload_directory / filename
        destination.write_bytes(image_bytes)
        storage_path = destination.relative_to(storage_root).as_posix()
        images.append({"image_id": image_id, "storage_path": storage_path})

    vision_client = VisionClient(
        api_key=settings.gemini_vision_key,
        model=settings.gemini_vision_model or None,
    )
    result = MediaProcessor(
        storage_root=str(storage_root),
        vision_client=vision_client,
    ).process(product_id, images)
    validate_media_output(result)
    return result
