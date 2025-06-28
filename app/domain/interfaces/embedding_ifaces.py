from abc import ABC, abstractmethod
from typing import Protocol


class IEmbeddingClient(Protocol):
    async def embed(self, text: str) -> list[float]:
        """Получить эмбеддинг для переданного текста."""
        ...


class IEmbeddingService(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Получить эмбеддинг для переданного текста."""
        ...
