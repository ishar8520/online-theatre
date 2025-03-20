from dependencies import get_shortener_service
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from models import ShortenRequest, ShortenResponse
from services.shortener import ShortenerService

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(
    request: ShortenRequest,
    shortener_service: ShortenerService = Depends(get_shortener_service),
):
    short_code = await shortener_service.create_short_url(request.url, request.user_id)
    return {"short_url": f"http://localhost:8000/{short_code}"}


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    shortener_service: ShortenerService = Depends(get_shortener_service),
):
    url = await shortener_service.get_original_url(short_code)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found or expired")
    return RedirectResponse(url=url)
