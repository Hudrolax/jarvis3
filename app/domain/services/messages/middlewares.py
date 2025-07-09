from typing import Annotated

from domain.interfaces.user_ifaces import IUserService
from domain.models.message import Message
from domain.models.user import UserDict

from .dependencies import get_user_service
from .domain_router import DomainMessageRouter
from .injector import Depends
from infrastructure.db.db import get_db 

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

middleware = DomainMessageRouter()


@middleware.message()
async def auth_middleware(
    msg: Message,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    print('middleware works')
    result = await db.execute(select(1))
    print('result', result.first())
    await msg.answer(Message(text='HELLLOOOOOO'))
