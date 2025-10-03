from __future__ import annotations

from typing import Annotated, Iterator

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from starlette import status

from app.api.v1.data_model import User as UserDto
from src.db import new_db_session
from src.multitenancy.user import get
from src.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/authentication/token")


def user_from_id(user_id: int) -> UserDto | None:
    with new_db_session(Settings.database.shared_schema) as session:
        if user := get(session, user_id):
            return UserDto(
                username=user.name,
                user_id=user.id,
                email=user.email,
                full_name=user.name,
                tenant_schema=user.tenant.schema,
            )
        return None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserDto:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            Settings.security_settings.secret_key,
            algorithms=[Settings.security_settings.algorithm],
        )
        user_id = int(payload.get("sub"))
        if user_id and (user := user_from_id(user_id)):
            return user
        raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception


def get_authenticated_session(
    current_user: Annotated[UserDto, Depends(get_current_user)],
) -> Iterator[Session]:
    with new_db_session(current_user.tenant_schema) as s:
        yield s
