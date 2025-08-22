from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.graph.state import CompiledStateGraph
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_node import ToolNode
# from langgraph.checkpoint.sqlite import SqliteSaver, Async
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
from langchain_core.messages.utils import trim_messages
from enum import Enum
from prompts.playwriter_prompts import stageplay_system_message, synopsis_message, ending_message
from agent_tools.characters import create_character
from agent_tools.human_in_the_loop import human_assistance
from db.handler import get_roster



class ContextLength(Enum):
    very_short = 5
    short = 15
    medium = 50 
    long = 100

class StagePlayState(TypedDict):
    line: int
    chapter : int
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
        self.chapter_length = ContextLength.short.value
        self.current_synopsis = None
        self.chapter_continue_message = "Narrator: "

        self.tools = [create_character, human_assistance] 
        self.llm = llm.bind_tools(self.tools)

        # Graph components
        self.tool_node = ToolNode(tools=self.tools, messages_key="context")

        self.story = []
    
    
    def system_message(self, line_count: int, synopsis: list[str] | None):
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
                                                                line_count= line_count,
                                                                number_of_lines= self.chapter_length,
                                                                synopsis= synopsis                               
                                                                ))

    def write_lines(self, state: StagePlayState):
        """Call agent to write new lines
        """  

        # Get messages from chapter start onwards
        messages = state["context"][self.chapter_length*state["chapter"]:]

        #Use trim function to ensure messages gives a vaild llm call
        trimmed_context = trim_messages(
            messages= messages,
            max_tokens=self.chapter_length, 
            strategy="last",  # Keeps recent messages
            token_counter=len,
            start_on="human",  # Ensures trimmed history starts with HumanMessage (or System + Human)
            include_system=False,  # Preserve SystemMessage if present (e.g., for prompts)
            allow_partial=False,  # Don't split individual messages
        )
        
        reply = self.llm.invoke([
                self.system_message(line_count= state["line"],
                                                  synopsis=self.current_synopsis),  # type: ignore
                *trimmed_context 
                ])
        return {"line": state["line"] + 1, "context": reply}

    def new_chapter(self, state: StagePlayState):
        """ Write a synopsis for the current state of the manuscript
        and start a new chapter
        """ 
        # Get messages from current chapter onwards
        messages = state["context"][self.chapter_length*state["chapter"]:]

        reply = self.llm.invoke([
            synopsis_message(),
            *messages  # type: ignore
        ])

        # Add previous lines to history
        # Note: we start chapter count at 1
        idx_end = state["chapter"]*self.chapter_length
        idx_start =  idx_end - self.chapter_length
        assert(idx_start >= 0)
        self.story.extend([line for line in state["context"][idx_start : idx_end]
                            if isinstance(line, (HumanMessage, AIMessage))])

        if self.current_synopsis is None:
            self.current_synopsis =[reply.content]
        else:
            self.current_synopsis.append(reply.content) 
        return {"line": 0, 
                "chapter": state["chapter"] +1,
                "context": HumanMessage(self.chapter_continue_message)}

    def write_ending(self, state: StagePlayState):
        """ Finish the play 
        """
        # Get messages from current chapter onwards
        messages = state["context"][self.chapter_length*state["chapter"]:]

        reply = self.llm.invoke([
            ending_message(),
            *messages  # type: ignore
        ])
        idx_start = state["chapter"]*self.chapter_length
        self.story.extend([line for line in state["context"][idx_start:]] + [reply.content]) 
        return {"line": 0, "chapter": 0 ,"context": reply}


    # Define the conditional edge that routes graph logic
    def routing_edge(self, state: StagePlayState):
        messages = state["context"]
        last_message: AnyMessage = messages[-1]
        # If there is no function call, then we continue to generating new line
        if not last_message.tool_calls:  # type: ignore[attr-defijned]
            if state["line"] >= self.chapter_length:
                if state["chapter"] >= self.number_of_chapters:
                   return "end"
                else:
                   return "new_chapter"
            else:
                return "continue"
        else: 
            return "go_to_tool"


    def build_graph(self, checkpointer)-> CompiledStateGraph:
        builder = StateGraph(StagePlayState)
        builder.add_node("write_lines_node", self.write_lines)
        builder.add_node("tool_node", self.tool_node)
        builder.add_node("new_chapter_node", self.new_chapter)
        builder.add_node("ending_node", self.write_ending)
        builder.set_entry_point("write_lines_node")
        builder.add_conditional_edges(
            "write_lines_node",
            self.routing_edge,
            {
                "go_to_tool": "tool_node",
                "continue": "write_lines_node",
                "new_chapter": "new_chapter_node",
                "end": "ending_node",
            },
        )
        builder.add_edge("tool_node", "write_lines_node")
        builder.add_edge("ending_node", END)
        return builder.compile(checkpointer= checkpointer)


def input_message(message : str) -> StagePlayState:
    """ Initialize an input message to invoke 
    agent graph
    """
    inputs = StagePlayState(
        line=0,
        chapter= 1,
        context=[
            HumanMessage(
                message 
            )
        ],
    )
    return inputs