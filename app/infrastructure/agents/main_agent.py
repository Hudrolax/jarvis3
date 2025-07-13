from typing import Callable

from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from domain.interfaces import IAgent
from domain.models import Message

from .llm_models import ToolsCallingModel


class Agent(IAgent):
    agent: CompiledStateGraph
    llm_model: str = ToolsCallingModel.GPT4oMini.value

    def __init__(
        self,
        system_message: str = '',
        tools: list[Callable] = [],
    ) -> None:
        llm = ChatOpenAI(model=self.llm_model, temperature=0)
        self.agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=system_message
        )

    async def invoke(self, msg: Message) -> Message:
        query = msg.text
        state = await self.agent.ainvoke({"messages": [("human", query)]})

        final_answer = state["messages"][-1].content
        return Message(text=final_answer)

