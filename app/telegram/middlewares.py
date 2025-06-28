from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware


class SomeService:
    async def some_func(self):
        print("some async func")


class InjectServicesMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]], event, data: Dict[str, Any]
    ) -> Any:
        print("middleware")
        data["some_service"] = SomeService()
        return await handler(event, data)
