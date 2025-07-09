# domain/services/messages/injector.py
import asyncio
import inspect
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Annotated, get_args, get_origin

logger = logging.getLogger(__name__)

class Depends:
    def __init__(self, dependency):
        self.dependency = dependency


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


def call_with_dependencies(func, *call_args, **call_kwargs):
    """
    Рекурсивно разрешает синхронные зависимости через Depends.
    """
    sig = inspect.signature(func)
    bound = sig.bind_partial(*call_args, **call_kwargs)
    kwargs = dict(bound.arguments)
    cleanup_ctxs = []

    for name, param in sig.parameters.items():
        if name in kwargs:
            continue

        # ищем Depends в default или в Annotated
        dep_marker = param.default if isinstance(param.default, Depends) else None
        if dep_marker is None:
            ann = param.annotation
            if get_origin(ann) is Annotated:
                for meta in get_args(ann)[1:]:
                    if isinstance(meta, Depends):
                        dep_marker = meta
                        break
        if dep_marker is None:
            continue

        dep = dep_marker.dependency
        if inspect.isgeneratorfunction(dep):
            cm = generator_context(dep)()
            val = cm.__enter__()
            cleanup_ctxs.append(cm)
        else:
            val = call_with_dependencies(dep)

        kwargs[name] = val

    result = func(**kwargs)

    for cm in reversed(cleanup_ctxs):
        cm.__exit__(None, None, None)

    return result


def service_injector(func):
    """
    Декоратор для асинхронных хендлеров:
    - Впрыскивает зависимости из sync- и async-генераторов
    - Автоматически вызывает __enter__/__exit__ и __anext__
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        injections = dict(bound.arguments)

        sync_ctxs = []
        async_gens = []

        # Разрешаем зависимости
        for name, param in sig.parameters.items():
            if name in injections:
                continue

            dep_marker = param.default if isinstance(param.default, Depends) else None
            if dep_marker is None:
                ann = param.annotation
                if get_origin(ann) is Annotated:
                    for meta in get_args(ann)[1:]:
                        if isinstance(meta, Depends):
                            dep_marker = meta
                            break
            if dep_marker is None:
                continue

            dep = dep_marker.dependency

            # Синхронный generator -> contextmanager
            if inspect.isgeneratorfunction(dep):
                cm = generator_context(dep)()
                val = cm.__enter__()
                sync_ctxs.append(cm)

            # Асинхронный generator
            elif inspect.isasyncgenfunction(dep):
                agen = dep()
                val = await agen.__anext__()
                async_gens.append(agen)

            # Обычная функция/корутина
            else:
                val = call_with_dependencies(dep)

            injections[name] = val

        # Вызываем целевую функцию
        result = func(**injections)
        if asyncio.iscoroutine(result):
            result = await result

        # Завершаем async-генераторы
        for agen in reversed(async_gens):
            try:
                await agen.__anext__()
            except StopAsyncIteration:
                pass

        # Завершаем sync-контексты
        for cm in reversed(sync_ctxs):
            cm.__exit__(None, None, None)

        return result

    return wrapper
