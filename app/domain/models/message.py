from datetime import datetime
from typing import Awaitable, Callable

from pydantic import ConfigDict, Field, field_serializer

from config import settings

from .base_domain_model import BaseDomainModel

AnswerType = Callable[["Message"], Awaitable[None]]


async def _default_answer(*_) -> None:
    return None

class Context(BaseDomainModel):
    model_config = ConfigDict(
        # чтобы .model_dump_json() сразу возвращал JSON-строку
        populate_by_name=True  
    )
    date: datetime = Field(default_factory=lambda: datetime.now(tz=settings.TZ), description='Дата сообщений')
    username: str = Field(..., description='Имя пользователя')
    user_text: str = Field(..., description='Текст пользователя')
    jarvis_text: str = Field(..., description='Ответ Jarvis')

    @field_serializer('date')
    def fmt_date(self, dt: datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class Message(BaseDomainModel):
    text: str
    user_id: int | None = None
    chat_id: int | None = None
    username: str | None = None
    answer: AnswerType = Field(default=_default_answer, description="Метод для ответа на сообщение")
    data: dict = Field(
        default_factory=dict, description="Словарь с дополнительными данными, которые могут прикреплять middleware."
    )
    context: list[Context] = Field(default_factory=list, description='Контекст диалога')
