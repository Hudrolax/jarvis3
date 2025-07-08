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
    sig = inspect.signature(func)
    bound = sig.bind_partial(*call_args, **call_kwargs)
    kwargs = dict(bound.arguments)
    cleanup_ctxs = []

    for name, param in sig.parameters.items():
        if name in kwargs:
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
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = call_with_dependencies(func, *args, **kwargs)
        # если результат — coroutine, дождёмся его
        if asyncio.iscoroutine(result):
            return await result
        return result

    return wrapper
