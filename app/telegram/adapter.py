from aiogram import Dispatcher
from aiogram.types import Message

from domain.models.message import Message as DomainMessage
from domain.services.messages.domain_router import DomainMessageRouter
from domain.services.messages.routers import router as test_router

domain_router = DomainMessageRouter()
domain_router.include_router(test_router)


def apply_dispatcher_adapter(dp: Dispatcher) -> None:
    @dp.message()
    async def _(msg: Message):
        async def answer_method(answer: DomainMessage) -> None:
            await msg.answer(answer.text)

        dm = DomainMessage(
            text=msg.text or "",
            chat_id=msg.chat.id,
            answer=answer_method,
        )
        await domain_router.dispatch(dm)
