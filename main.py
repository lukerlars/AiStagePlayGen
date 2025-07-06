from langgraph.graph import StateGraph, START, END, add_messages
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated, Sequence
from langchain_core.tools import tool 
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import (
    AnyMessage,
    BaseMessage, 
    AIMessage, 
    HumanMessage, 
    SystemMessage,
    ToolMessage
    )
import operator
from dotenv import load_dotenv
import json
from characters import characters

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
retrieve and store new information about characters.  

""")

llm = ChatOpenAI(model = "gpt-4o-mini")
checkpointer = InMemorySaver()
graph_config = {"configurable": {"thread_id": "1"}}


class StagePlayState(TypedDict):
    context: Annotated[Sequence[BaseMessage], add_messages]


## tool callling 
@tool
def get_character_description(character_name: str):
    """Get a short description for a character"""
    # TODO make better descriptions: add more thorough characted desc
    # to character dataclass 
    return str(characters[character_name])



def call_llm(state: StagePlayState, config: RunnableConfig):
    reply = llm.invoke([system_message, *state["context"]])
    return {"context": reply}



tools = [get_character_description]
llm = llm.bind_tools(tools)


tool_node = ToolNode(tools= tools, messages_key= "context")

# Define the conditional edge that determines whether to continue or not
def should_continue(state: StagePlayState):
    messages = state["context"]
    last_message = messages[-1]
    # If there is no function call, then we continue to generating new line
    if not last_message.tool_calls:
        if len(messages) > 15:
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

graph = builder.compile()

def print_stream(stream):
    for s in stream:
        message = s["context"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


if __name__ == "__main__":
    inputs = {"context": """Narrator: It is a sunny wistful day in Tam Tamouree,
                           Swedenborg and Luna lazily scout over the townspeople from their hidden 
                           vantage point atop the old church.
                           Luna:
                           """}
    print_stream(graph.stream(inputs, stream_mode="values"))
    