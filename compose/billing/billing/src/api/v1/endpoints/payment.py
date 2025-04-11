from __future__ import annotations

from http import HTTPStatus

from fastapi import APIRouter

router = APIRouter()


@router.post(
    path='/create',
    status_code=HTTPStatus.CREATED,
    summary='New purchase'
)
async def create():
    pass
