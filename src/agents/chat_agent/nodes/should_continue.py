from typing_extensions import Literal
from langgraph.graph import END
from src.agents.chat_agent.states.chat_agent_state import ChatAgentState


def should_continue(state: ChatAgentState) -> Literal["tool_executer_node", END]: # type: ignore
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
    messages = state["message"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tool_executer_node"
    return END
