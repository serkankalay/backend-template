from __future__ import annotations

from http import HTTPStatus

from fastapi import APIRouter

api = APIRouter(tags=["Health Check"])


@api.get("/health-check", status_code=HTTPStatus.NO_CONTENT)
def health_check():
    return
