from langgraph.types import interrupt
from langchain_core.tools import tool 

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human.
    query : Ask human for next line"""
    human_response = interrupt({"query": query})
    return human_response["data"]