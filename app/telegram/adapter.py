from aiogram import Dispatcher
from aiogram.types import Message

from domain.models.message import Message as DomainMessage
from domain.services.messages.main_router import main_router


def apply_dispatcher_adapter(dp: Dispatcher) -> None:
    @dp.message()
    async def _(msg: Message):
        async def answer_method(answer: DomainMessage) -> None:
            await msg.answer(answer.text)

        dm = DomainMessage(
            text=msg.text or "",
            user_id=msg.from_user.id if msg.from_user else None,
            chat_id=msg.chat.id,
            username=msg.from_user.username if msg.from_user else None,
            answer=answer_method,
        )
        await main_router.dispatch(dm)
