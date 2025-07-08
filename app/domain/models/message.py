from typing import Annotated, Awaitable, Callable

AnswerType = Callable[["Message"], Awaitable[None]]


async def _default_answer(*_) -> None:
    return None


class Message:
    def __init__(
        self,
        text: Annotated[str, "Текст сообщения"],
        chat_id: Annotated[int | None, "ID чата"] = None,
        answer: Annotated[AnswerType, "Метод ответа на сообщение"] = _default_answer,
    ) -> None:
        self.text = text
        self.chat_id = chat_id
        self.answer = answer

    def __str__(self) -> str:
        return f'Message(text={self.text}, chat_id={self.chat_id})'
