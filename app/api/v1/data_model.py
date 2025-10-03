from __future__ import annotations

from pydantic import BaseModel


class Token(BaseModel):
    token_type: str
    access_token: str


class User(BaseModel):
    username: str
    user_id: int
    password: str | None = None
    email: str | None = None
    full_name: str | None = None
    tenant_schema: str
