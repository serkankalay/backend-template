from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.api.v1.data_model import Token
from app.api.v1.data_model import User as UserDto
from app.api.v1.security.common import get_current_user, oauth2_scheme
from src.data_model import User
from src.db import get_shared_db_session
from src.multitenancy.user import try_get
from src.settings import Settings

logger = logging.getLogger(__name__)

api = APIRouter(prefix="/authentication", tags=["Security"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _authenticate(
    session: Session,
    username: str,
    password: str,
) -> User | None:
    if (user := try_get(session, username)) and _verify_password(
        password, user.password
    ):
        return user
    return None


def _create_token(
    user_id: int,
    expires_delta: timedelta,
) -> str:
    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + expires_delta,
        },
        Settings.security_settings.secret_key,
        algorithm=Settings.security_settings.algorithm,
    )


@api.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auto_refresh: bool = Form(default=True),
    session: Session = Depends(get_shared_db_session),
) -> JSONResponse:
    if not (
        user := _authenticate(
            session,
            form_data.username,
            form_data.password,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = Token(
        access_token=_create_token(
            user_id=user.id,
            expires_delta=timedelta(
                minutes=Settings.security_settings.access_token_expire_mins
            ),
        ),
        token_type="bearer",
    )

    response = JSONResponse(content=token.model_dump())
    if auto_refresh:
        response.set_cookie(
            key="refresh_token",
            value=_create_token(
                user_id=user.id,
                expires_delta=timedelta(
                    minutes=Settings.security_settings.refresh_token_expire_mins  # noqa: E501
                ),
            ),
            httponly=True,
            # TODO: introduce Environment for secure flag
            secure=False,  # Only over HTTPS
            path="/",  # Visible to Django
            samesite="lax",
            max_age=Settings.security_settings.refresh_token_expire_mins * 60,
        )

    return response


@api.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str = Cookie(None)) -> Token:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing refresh token.",
        )
    try:
        payload = jwt.decode(
            refresh_token,
            Settings.security_settings.secret_key,
            algorithms=[Settings.security_settings.algorithm],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return Token(
            access_token=_create_token(
                user_id=user_id,
                expires_delta=timedelta(
                    minutes=Settings.security_settings.access_token_expire_mins
                ),
            ),
            token_type="bearer",
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )


@api.get("/users/me", response_model=UserDto)
async def who_am_i(
    user: Annotated[UserDto, Depends(get_current_user)],
) -> UserDto:
    return user


@api.get("/ping", status_code=HTTPStatus.OK)
async def ping(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(
            token,
            Settings.security_settings.secret_key,
            algorithms=[Settings.security_settings.algorithm],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
