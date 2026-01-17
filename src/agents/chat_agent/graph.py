from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from src.agents.chat_agent.nodes.chat_node import chat
from src.agents.chat_agent.states.chat_agent_state import ChatAgentState
from langgraph.checkpoint.memory import MemorySaver
from src.agents.chat_agent.nodes.should_continue import should_continue
from src.agents.chat_agent.nodes.tool_executer_node import tool_executer


checkpointer = MemorySaver()


def create_chat_agent_graph() -> CompiledStateGraph:
    """Create a chat agent graph"""
    graph_builder = StateGraph(ChatAgentState)
    graph_builder.add_node("chat_node", chat)
    graph_builder.add_node("tool_executer_node", tool_executer)
    graph_builder.add_edge(START, "chat_node")
    graph_builder.add_conditional_edges(
        "chat_node",
        should_continue,
    )
    graph_builder.add_edge("tool_executer_node", "chat_node")
    return graph_builder.compile(checkpointer=checkpointer)
