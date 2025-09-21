from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import VERSION
from app.api.v1.health_check import api as api_health_check
from src.logging.main import init_logging

init_logging("config/logging_backend.yml")


app = FastAPI(
    title="Application API",
    description="Backend for the application.",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    openapi_tags=[
        {
            "name": "Application API",
            "description": "The API that enables communication between the apps and backend.",  # noqa: E501
        }
    ],
    version=VERSION,
)

app.include_router(api_health_check, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # your Django frontend URL
    allow_credentials=True,  # allow cookies!
    allow_methods=["*"],
    allow_headers=["*"],
)
