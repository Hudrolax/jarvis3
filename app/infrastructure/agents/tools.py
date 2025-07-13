import asyncio

from langchain_core.tools import tool


@tool()
async def add_link_tool(link: str) -> str:
    """Добавляет ссылку в базу данных."""
    print('вызвано добавление ссылки')
    await asyncio.sleep(0.1)
    return "Ссылка добавлена"
