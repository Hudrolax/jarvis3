from datetime import datetime
from pprint import pprint as print
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

chain = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class Link(BaseModel):
    """Данные о ссылке"""

    name: Optional[str] = Field(None, description="Имя")
    surname: Optional[str] = Field(None, description="Фамилия")
    birth_date: Optional[datetime] = Field(None, description="Дата рождения")
    preferences: Optional[str] = Field(None, description="Предпочтения человека")


structured_llm = chain.with_structured_output(Person)
system_msg = SystemMessage(
    content="""
Извлекай данне о человеке из текста и возвращай их в структурированном виде.
Не придумывай факты. Если данных для поля нет - вставляй None
"""
)


def preprocessing(data: list[str]) -> list[Person]:
    result = []
    for query in data:
        human_msg = HumanMessage(query)
        result.append(structured_llm.invoke([system_msg, human_msg]))
    return result


data = [
    """
    Что за человек Сиплый Иван? Это тот, которому сегодня ровно 35 лет (а сегодня 20 июня 2025 года).
    И тот, который любит курить трубку.
    """,
    """
    Что мы знаем о Жоре? Да в принципе ничего

    """,
]

output = preprocessing(data)
print(output)
