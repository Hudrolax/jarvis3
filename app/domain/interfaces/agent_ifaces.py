from abc import ABC, abstractmethod
from typing import Callable

from domain.models.message import Message


class IAgent(ABC):
    @abstractmethod
    def __init__(
        self,
        tools: list[Callable] = [],
        system_message: str = '',
    ) -> None:
        """
        Инициализирует агент с набором инструментов и системным сообщением.

        Args:
            tools (list[Callable], optional): Список вызываемых инструментов, которые агент может использовать.
                По умолчанию пустой список.
                tools должны быть декорированы декторатором @tool()
            system_message (str, optional): Сообщение системы, задающее контекст или инструкции для агента.
                По умолчанию пустая строка.

        Returns:
            None
        """
        ...

    @abstractmethod
    async def invoke(self, msg: Message) -> Message:
        """Вызвает агента и передает ему сообщение. Агент должен ответить сообжением."""
        ...
