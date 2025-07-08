from typing import Annotated

from domain.models.message import Message

from .domain_router import DomainMessageRouter
from .injectors import Depends, service_injector

router = DomainMessageRouter()

class SomeClass:
    async def bark(self):
        print('bark!!!!!!')


def service_factory():
    yield SomeClass()
    print('Очистка после гавка')


@router.message(lambda m: m.text == "hello")
@service_injector
async def domain_route(
    msg: Message,
    some_service: Annotated[SomeClass, Depends(service_factory)]
):
    print(msg)
    await some_service.bark()
    await msg.answer(Message(text='HELLLOOOOOO'))


@router.message(lambda m: m.text == "test")
async def test_router(msg: Message):
    print(msg)
    await msg.answer(Message(text='Teeest'))
