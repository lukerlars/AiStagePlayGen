from langgraph.graph import StateGraph, START, END, add_messages
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_node import ToolNode
# from langgraph.checkpoint.sqlite import SqliteSaver, Async
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from typing import TypedDict, Annotated 
from langchain_core.messages import (
    AnyMessage,
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    ToolCall,
)
# import sqlite3
import aiosqlite
from langchain_core.messages.utils import trim_messages
from enum import Enum
from prompts.playwriter_sysprompt import stageplay_system_message
from agent_tools.characters import create_character
from agent_tools.human_in_the_loop import human_assistance
from db.handler import get_roster

class ContextLength(Enum):
    very_short = 5
    short = 15
    medium = 50 
    long = 100

class StagePlayState(TypedDict):
    counter: int
    context: Annotated[list[AnyMessage], add_messages]


class StagePlayWriter:

    def __init__(self, 
                 llm: ChatOpenAI,
                 themes : str,
                 vibe : str,
                 setting: str,
                 number_of_chapters : int,
                ):
        """Initialize stage play writer
        agent graph""" 
        self.themes = themes
        self.vibe = vibe
        self.setting = setting
        self.number_of_chapters = number_of_chapters
        self.current_chapter = 1

        # self.sqlite_connection = sqlite3.connect("db/graph_checkpoints/checkpoints.db",
        #                                                 check_same_thread=False)
        # # self.checkpointer = SqliteSaver(self.sqlite_connection)

        self.tools = [create_character, human_assistance] 
        self.llm = llm.bind_tools(self.tools)

        # Graph components
        self.tool_node = ToolNode(tools=self.tools, messages_key="context")

        # #Build graph
        # self.graph = self.build_graph(checkpointer= self.checkpointer)

    
    def system_message(self, synopsis: str | None):
        """Get dynamic system message
        This message gets passed at the start to every query to the llm
        """
        roster = get_roster()
        return SystemMessage(content= stageplay_system_message(tools=self.tools,
                                                                roster=roster,
                                                                themes=self.themes,
                                                                vibe= self.vibe,
                                                                setting= self.setting,
                                                                number_of_chapters= self.number_of_chapters,
                                                                current_chapter= self.current_chapter,
                                                                synopsis= synopsis                               
                                                                ))

    def call_llm(self ,state: StagePlayState):
        """Call llm"""
        trimmed_context = trim_messages(
            messages=state["context"],
            max_tokens=ContextLength.medium.value, 
            strategy="last",  # Keeps recent messages
            token_counter=len,
            start_on="human",  # Ensures trimmed history starts with HumanMessage (or System + Human)
            include_system=False,  # Preserve SystemMessage if present (e.g., for prompts)
            allow_partial=False,  # Don't split individual messages
        )
        reply = self.llm.invoke([self.system_message(synopsis=None), *trimmed_context])
        return {"counter": state["counter"] + 1, "context": reply}
   
 
    # Define the conditional edge that determines whether to continue or not
    def should_continue(self,state: StagePlayState):
        messages = state["context"]
        counter = state["counter"]
        last_message: AnyMessage = messages[-1]
        # If there is no function call, then we continue to generating new line
        if not last_message.tool_calls:  # type: ignore[attr-defined]
            if counter > ContextLength.very_short.value:
                return "end"
            else:
                return "continue"
        # Otherwise if there is, we continue
        else: 
            return "continue_to_tool"
 
    def build_graph(self, checkpointer):
        builder = StateGraph(StagePlayState)
        builder.add_node("llm_node", self.call_llm)
        builder.add_node("tool_node", self.tool_node)

        builder.set_entry_point("llm_node")
        builder.add_conditional_edges(
            "llm_node",
            self.should_continue,
            {
                "continue_to_tool": "tool_node",
                "continue": "llm_node",
                "end": END,
            },
        )
        builder.add_edge("tool_node", "llm_node")

        return builder.compile(checkpointer= checkpointer)


