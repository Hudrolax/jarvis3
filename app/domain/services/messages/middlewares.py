from typing import Annotated

from dependencies import get_user_service
from domain.exceptions import NotFoundError
from domain.interfaces.user_ifaces import IUserService
from domain.models import Message
from infrastructure.deps_injector import Depends

from .domain_router import DomainMessageRouter

middleware = DomainMessageRouter()


@middleware.message()
async def auth_middleware(
    msg: Message,
    user_service: Annotated[IUserService, Depends(get_user_service)]
):
    try:
        user = await user_service.read(filters={'telegram_id': msg.user_id})
        msg.data['user'] = user
    except NotFoundError:
        await msg.answer(Message(text='Я тебя не знаю'))
        raise NotFoundError(f'Пользователь с телеграм id {msg.user_id} не найден в базе.')
