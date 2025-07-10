from typing import Annotated

from domain.exceptions import NotFoundError
from domain.interfaces.user_ifaces import IUserService
from domain.models import Message

from .dependencies import get_user_service
from .domain_router import DomainMessageRouter
from .injector import Depends

middleware = DomainMessageRouter()


@middleware.message()
async def auth_middleware(
    msg: Message,
    user_service: Annotated[IUserService, Depends(get_user_service)]
):
    try:
        await user_service.read(filters={'telegram_id': msg.user_id})
    except NotFoundError:
        await msg.answer(Message(text='Я тебя не знаю'))
        raise NotFoundError(f'Пользователь с телеграм id {msg.user_id} не найден в базе.')
