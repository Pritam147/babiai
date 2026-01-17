import time
from langchain.tools import tool

@tool
def get_current_datetime() -> str:
    """Use this to get the current date and time"""
    return time.ctime()