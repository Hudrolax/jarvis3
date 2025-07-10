from typing import Annotated, Awaitable, Callable

from .base_domain_model import BaseDomainModel

AnswerType = Callable[["Message"], Awaitable[None]]


async def _default_answer(*_) -> None:
    return None

class Message(BaseDomainModel):
    text: str
    user_id: int | None = None
    chat_id: int | None = None
    username: str | None = None
    answer: Annotated[AnswerType, 'Метод для ответа на сообщение'] = _default_answer

# TODO: очистить
#
# class Message:
#     def __init__(
#         self,
#         text: Annotated[str, "Текст сообщения"],
#         user_id: Annotated[int | None, "ID пользователя"] = None,
#         chat_id: Annotated[int | None, "ID чата"] = None,
#         username: Annotated[str | None, "username пользователя"] = None,
#         answer: Annotated[AnswerType, "Метод ответа на сообщение"] = _default_answer,
#     ) -> None:
#         self.text = text
#         self.user_id = user_id,
#         self.chat_id = chat_id
#         self.username = username,
#         self.answer = answer
#
#     def __str__(self) -> str:
#         return f'Message(text={self.text}, chat_id={self.chat_id})'
