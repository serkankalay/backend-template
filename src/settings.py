from __future__ import annotations

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class TimeSettings(BaseSettings):
    local_timezone: str = Field(validation_alias="TIMEZONE_LOCAL")
    server_timezone: str = Field(validation_alias="TIMEZONE_SERVER")


class SecuritySettings(BaseSettings):
    secret_key: str = Field(validation_alias="AUTH_SECRET_KEY")
    algorithm: str = Field(validation_alias="AUTH_ALGORITHM")
    access_token_expire_mins: int = Field(
        validation_alias="AUTH_ACCESS_EXPIRE_MINUTES"
    )
    refresh_token_expire_mins: int = Field(
        validation_alias="AUTH_REFRESH_EXPIRE_MINUTES"
    )


class DatabaseSettings(BaseSettings):
    pg_dsn: PostgresDsn = Field(validation_alias="DB_URL")
    shared_schema: str = Field(validation_alias="SHARED_SCHEMA_NAME")


class AppSettings(BaseSettings):
    redis_dsn: RedisDsn = Field(validation_alias="REDIS_URL")
    time_settings: TimeSettings = Field(
        default_factory=TimeSettings  # type: ignore
    )
    security_settings: SecuritySettings = Field(
        default_factory=SecuritySettings  # type: ignore
    )
    database: DatabaseSettings = Field(
        default_factory=DatabaseSettings  # type: ignore
    )


Settings: AppSettings = AppSettings()  # type: ignore
