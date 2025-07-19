import asyncio
import inspect
import logging
import sys
from contextlib import AbstractContextManager, contextmanager
from functools import wraps
from typing import Annotated, Any, AsyncGenerator, get_args, get_origin

from domain.interfaces.message_router_iface import Handler

logger = logging.getLogger(__name__)

class Depends:
    def __init__(self, dependency):
        self.dependency = dependency

def use_services():
    """
    Decorator for service injection
    """
    def decorator(fn: Handler) -> Handler:
        wrapped = service_injector(fn)
        return wrapped
    return decorator


def generator_context(func):
    """
    Преобразует синхронный generator-функцию в contextmanager,
    чтобы поддерживать зависимость через yield.
    """
    @contextmanager
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        try:
            value = next(gen)
        except StopIteration:
            raise RuntimeError("Генератор ничего не yield'ит")
        try:
            yield value
        finally:
            try:
                next(gen)
            except StopIteration:
                pass

    return wrapper


def service_injector(func):
    """
    Рекурсивно резолвит Depends‑зависимости и корректно
    освобождает все контексты (sync и async).
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sync_ctxs: list[AbstractContextManager] = []
        async_gens: list[AsyncGenerator] = []

        async def resolve_dep(dep_func):
            # 1) sync‑generator → contextmanager
            if inspect.isgeneratorfunction(dep_func):
                cm = generator_context(dep_func)()
                val = cm.__enter__()
                sync_ctxs.append(cm)
                return val

            # 2) async‑generator
            if inspect.isasyncgenfunction(dep_func):
                agen = dep_func()
                val = await agen.__anext__()
                async_gens.append(agen)
                return val

            # 3) обычная функция / coroutine с вложенными Depends
            sig_dep = inspect.signature(dep_func)
            kwargs_dep: dict[str, Any] = {}

            for pname, pparam in sig_dep.parameters.items():
                dep_marker = pparam.default if isinstance(pparam.default, Depends) else None
                if dep_marker is None and get_origin(pparam.annotation) is Annotated:
                    for meta in get_args(pparam.annotation)[1:]:
                        if isinstance(meta, Depends):
                            dep_marker = meta
                            break
                if dep_marker is not None:
                    kwargs_dep[pname] = await resolve_dep(dep_marker.dependency)

            result = dep_func(**kwargs_dep)
            if asyncio.iscoroutine(result):
                result = await result
            return result

        try:
            # резолвим параметры самого обрабатываемого хендлера
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            injections = dict(bound.arguments)

            for name, param in sig.parameters.items():
                if name in injections:
                    continue
                dep_marker = param.default if isinstance(param.default, Depends) else None
                if dep_marker is None and get_origin(param.annotation) is Annotated:
                    for meta in get_args(param.annotation)[1:]:
                        if isinstance(meta, Depends):
                            dep_marker = meta
                            break
                if dep_marker is not None:
                    injections[name] = await resolve_dep(dep_marker.dependency)

            # вызываем оригинальный хендлер
            result = func(**injections)
            if asyncio.iscoroutine(result):
                result = await result
            return result

        finally:
            # гарантированное закрытие ресурсов
            for agen in reversed(async_gens):
                try:
                    await agen.__anext__()
                except StopAsyncIteration:
                    pass
                except Exception:
                    await agen.aclose()

            for cm in reversed(sync_ctxs):
                cm.__exit__(*sys.exc_info())

    return wrapper
