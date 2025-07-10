import re
from typing import Annotated

from domain.interfaces import ILinkService
from domain.models import Message

from .dependencies import get_link_service
from .domain_router import DomainMessageRouter
from .injector import Depends

router = DomainMessageRouter()


@router.message(lambda m: bool(re.compile(r'https?://\S+').search(m.text)))
async def get_link_route(
    msg: Message,
    link_service: Annotated[ILinkService, Depends(get_link_service)]
):
    print(msg)
    print(msg.data)
    await msg.answer(Message(text='HELLLOOOOOO'))


# @router.message(lambda m: m.text == "test")
# async def test_router(msg: Message):
#     print('router works')
#     print(msg)
#     await msg.answer(Message(text='Teeest'))
