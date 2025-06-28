from pydantic import BaseModel, Field

from config.config import settings as core


class TelegramBotCfg(BaseModel):
    name: str
    token: str


class TelegramSettings(BaseModel):
    bots: list[TelegramBotCfg] = Field(..., description="Список запускаемых ботов")
    proxy: str | None = None  # если нужен прокси


telegram_settings = TelegramSettings.model_validate(core.TELEGRAM_BOTS)

