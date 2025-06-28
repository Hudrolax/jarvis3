from aiogram import F, Router
from aiogram.types import Message

from .middlewares import SomeService

router = Router()

@router.message(F.text == "/start")
async def cmd_start(msg: Message):
    await msg.answer("Привет! Я — бот #️⃣{msg.bot.id}")


@router.message(F.text == 'test')
async def test(msg: Message):
    await msg.answer('test')


@router.message(F.text == 'hello')
async def hello(msg: Message, some_service: SomeService):
    await some_service.some_func()
    await msg.answer('hello')
