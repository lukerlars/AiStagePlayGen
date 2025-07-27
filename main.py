from langgraph.graph import StateGraph, START, END, add_messages
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated, Sequence
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import (
    AnyMessage,
    BaseMessage, 
    AIMessage, 
    HumanMessage, 
    SystemMessage,
    ToolMessage,
    ToolCall
    )
from langchain_core.messages.utils import trim_messages
import operator
from dotenv import load_dotenv
import json
from characters import roster, Character, create_character, get_character_description 
from langchain_core.tools import tool 
from enum import Enum

load_dotenv()

system_message = SystemMessage(content="""
You are the co writer of a stage play
You recieve a story and write the continuation
You will recieve the current state of the play with a precursor of a role name.
This role will either be the role of the narrator or a character in the play.
When writing as the narrator you will continue the story by describing the
unfolding of events based on previous context. When writing for a character you 
will write the appropriate line with respect to the previous dialogue, context
and the characters persona.

Here is an example of how such a continuation will look:           

... (imagine some more previous context here)...
                               
Narrator: And so, our heroes set forth into the unknown. Their minds anxiously 
lingering on the place they've left behind and the uncertantiy that lies ahead.
Suddenly a faint sound is heard from the bushes

Jack : 

....

In this case the response should be the dialgoue spoken by the character Jack. 

To aide you with the writing process, you will be given access to tools to 
retrieve and store new information about characters. When you encounter
a character, you may call the get infromation tool to see information 
about the character.
You should feel free to create new charcters. Make sure to always store the charcter 
information using the tool, when introducing new characters. 

""")

llm = ChatOpenAI(model = "gpt-4o-mini")
checkpointer = InMemorySaver()
graph_config = {"configurable": {"thread_id": "1"}}

class ContextLength(Enum):
    very_short = 5 
    short = 15
    medium = 40
    long = 100


class StagePlayState(TypedDict):
    counter : int
    context: Annotated[list[AnyMessage], add_messages]


def call_llm(state: StagePlayState, config: RunnableConfig): 
    trimmed_context = trim_messages(
    messages=state["context"],
    max_tokens= ContextLength.medium.value,  # e.g., 4000; adjust for your model's windo
    strategy="last",  # Keeps recent messages
    token_counter=len,  
    start_on="human",  # Ensures trimmed history starts with HumanMessage (or System + Human)
    include_system=False,  # Preserve SystemMessage if present (e.g., for prompts)
    allow_partial=False  # Don't split individual messages
    ) 
    reply = llm.invoke([system_message, *trimmed_context])
    return {"counter": state["counter"] +1, "context": reply}


roster = roster
tools = [get_character_description, create_character]
llm = llm.bind_tools(tools)


tool_node = ToolNode(tools= tools, messages_key= "context")

# Define the conditional edge that determines whether to continue or not
def should_continue(state: StagePlayState):
    messages = state["context"]
    counter = state["counter"]
    last_message = messages[-1]
    # If there is no function call, then we continue to generating new line
    if not last_message.tool_calls:
        if counter > ContextLength.very_short.value:
           return "end"
        else:
           return "continue"
    # Otherwise if there is, we continue
    else:
        return "continue_to_tool"

builder = StateGraph(StagePlayState)


builder.add_node("llm_node", call_llm)
builder.add_node("tool_node", tool_node)

builder.set_entry_point("llm_node")
builder.add_conditional_edges(
    "llm_node",
    should_continue,
    {
        "continue_to_tool": "tool_node",
        "continue": "llm_node",
        "end": END,
    },
)
builder.add_edge("tool_node", "llm_node")

graph = builder.compile(checkpointer= checkpointer)

def print_stream(stream):
    for s in stream:
        message = s["context"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


if __name__ == "__main__":
    inputs = StagePlayState(
        counter= 0,
        context = [HumanMessage(
            """Narrator: It is a sunny wistful day in Tam Tamouree,
            Swedenborg and Luna lazily scout over the townspeople from their hidden vantage point atop the old church.
            Luna:
            """)]
            )
    
    print_stream(graph.stream(inputs, stream_mode="values", config = graph_config))
       
    # graph.invoke(inputs, config = graph_config)
