from datetime import datetime, timezone
from typing import Literal

from pydantic import Field

from .base_domain_model import BaseCreateDict, BaseDomainModel


class Link(BaseDomainModel):
    id: int = Field(..., description='ID в БД')
    user_id: int = Field(..., description='ID пользователя в БД')
    link: str = Field(..., description='Ссылка')
    description: str = Field("", description='Описание')
    title: str | None = Field(None, description='Заголовок (короткое описание)')
    created_at: datetime = Field(datetime.now(timezone.utc), description='Дата создания')
    pull_count: int = Field(0, description='Количество запросов ссылки')
    vector: list[float] | None = Field(None, description='Векторное представление ссылки')


class LinkDict(BaseCreateDict, total=False):
    id: int
    user_id: int
    link: str
    description: str
    title: str | None
    created_at: datetime
    pull_count: int
    vector: list[float] | None


LinkFields = Literal["id", "user_id", "link", "description", "title", "created_at", "pull_count", "vector"]
