from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from src.agents.chat_agent.states.chat_agent_state import ChatAgentState
from src.agents.chat_agent.tools.date_time import get_current_datetime

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def chat(state: ChatAgentState) -> ChatAgentState:

    model = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=GROQ_API_KEY,
    )
    model = model.bind_tools(
        [
            get_current_datetime,
        ]
    )
    answer = model.invoke(state["message"])
    return {"message": [answer]}
