from src.agents.chat_agent.states.chat_agent_state import ChatAgentState
from src.agents.chat_agent.tools.date_time import get_current_datetime
from langchain.messages import ToolMessage


tools = [get_current_datetime]

tools_by_name = {tool.name: tool for tool in tools}


def tool_executer(state: ChatAgentState) -> ChatAgentState:
    """Execute the tool calls made by the LLM in the last message"""
    
    result = []

    for tool_call in state["message"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])

        result.append(
            ToolMessage(
                content=observation,
                tool_call_id=tool_call["id"],
            )
        )

    return {"message": result}
