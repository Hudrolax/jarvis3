from typing import Awaitable, Callable

from pydantic import Field

from .base_domain_model import BaseDomainModel

AnswerType = Callable[["Message"], Awaitable[None]]


async def _default_answer(*_) -> None:
    return None


class Message(BaseDomainModel):
    text: str
    user_id: int | None = None
    chat_id: int | None = None
    username: str | None = None
    answer: AnswerType = Field(default=_default_answer, description="Метод для ответа на сообщение")
    data: dict = Field(
        default_factory=dict, description="Словарь с дополнительными данными, которые могут прикреплять middleware."
    )
