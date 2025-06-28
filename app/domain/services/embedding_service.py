from ..interfaces.embedding_ifaces import IEmbeddingClient, IEmbeddingService


class EmbeddingService(IEmbeddingService):
    def __init__(self, client: IEmbeddingClient) -> None:
        self.client = client

    async def embed(self, text: str) -> list[float]:
        """Получить эмбеддинг для переданного текста."""
        return await self.client.embed(text)
