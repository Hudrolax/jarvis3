from typing import Generic

from domain.models.base_domain_model import TDomain, TTypedDict
from domain.models.link import LinkDict, LinkFields

from ..db.models.base_model_orm import TOrm
from .sqlalchemy_mixins import (
    CreateMixin,
    DeleteMixin,
    ExistsMixin,
    ListMixin,
    ReadMixin,
    UpdateMixin,
    VectorSearchMixin,
)


class LinkRepo(
    CreateMixin[TDomain, TOrm, LinkDict],
    ReadMixin[TDomain, TOrm, LinkDict],
    UpdateMixin[TDomain, TOrm, LinkDict],
    ListMixin[TDomain, TOrm, LinkDict, LinkFields],
    ExistsMixin[TDomain, TOrm, LinkDict],
    DeleteMixin[TDomain, TOrm, LinkDict],
    VectorSearchMixin[TDomain, TOrm, LinkDict],
    Generic[TDomain, TOrm, TTypedDict],
): ...
