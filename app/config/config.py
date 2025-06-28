from typing import ClassVar, Literal
from zoneinfo import ZoneInfo

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevels = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # DB Settings
    DATABASE_URL: str = Field(..., description="DB URL")

    # TimeZone settings
    TZ: ZoneInfo = Field(ZoneInfo("UTC"), description="Временная зона")

    # Logging settings
    LOG_LEVEL: LogLevels = Field("INFO", description="Уровень логирования")

    # Security settings
    SECRET: str = Field(..., description="JWT secret")
    JWT_TOKEN_EXPIRE_MINUTES: int = Field(
        60 * 24 * 356 * 99,
        description="Время жизни JWT токена в минутах",
    )
    JWT_ALGORITHM: str = Field("HS256", description="Алгоритм шифрования JWT токена")

    # Telegram bots
    TELEGRAM_BOTS: dict[str, list[dict[str, str]]] = {
        "bots":[
            # {"name":"support_bot","token":"987:BBB"},
        ]
    }

    @field_validator("TZ", mode="before")
    @classmethod
    def _parse_tz(cls, v):
        return ZoneInfo(v) if isinstance(v, str) else v


settings = Settings()
