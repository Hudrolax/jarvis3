from typing import Annotated

from domain.interfaces.user_ifaces import IUserService
from domain.models import Message

from .dependencies import get_user_service
from .domain_router import DomainMessageRouter
from .injector import Depends

router = DomainMessageRouter()


@router.message(lambda m: m.text == "hello")
async def domain_route(
    msg: Message,
    user_service: Annotated[IUserService, Depends(get_user_service)]
):
    print('router works')
    print(msg)
    await msg.answer(Message(text='HELLLOOOOOO'))


@router.message(lambda m: m.text == "test")
async def test_router(msg: Message):
    print('router works')
    print(msg)
    await msg.answer(Message(text='Teeest'))
