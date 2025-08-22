import streamlit as st

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage, HumanMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent_graph import StagePlayWriter,input_message, StagePlayState
from langgraph.types import Command
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.sqlite import SqliteSaver
import time
from uuid import uuid4


load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")
# tools = [get_character_description, create_character, human_assistance]

thread_id = uuid4()

graph_config: RunnableConfig = RunnableConfig({"configurable": {"thread_id": thread_id}})

playwriter = StagePlayWriter(
    llm=llm,
    themes= """Loss of innocence, Becoming Psychologically whole, Jungian Psychology, Bildung""",
    vibe= """Subtly, Weird and funky""",
    setting= "Tam Tamoree, fictional town in German Bavaria",
    number_of_chapters= 4
)

conn_checkptr = "db/graph_checkpoints/checkpoints.db"


# Title
st.title("Playwriter")

# Text input box
user_input = st.text_input("Enter your text here:")
# Add button to submit text
if st.button("Start"):
    if user_input:
        with SqliteSaver.from_conn_string(conn_checkptr) as checkpointer:
            outer_event = [None]
            for event in (playwriter
                            .build_graph(checkpointer)
                            .stream(input=input_message(user_input), 
                                    config= graph_config, 
                                    stream_mode="values")): 
                context = event["context"][-1]
                # Add current message to state
                st.write(context.content)
                outer_event = event

        if "__interrupt__" in outer_event:
            second_input = st.text_input("Enter more text!")
            if st.button("continue"):
                if second_input:
                    for event in (playwriter
                                    .build_graph(checkpointer)
                                    .stream(input=input_message(user_input), 
                                            config= graph_config, 
                                            stream_mode="values")): 
                        context = event["context"][-1]
                        # Add current message to state
                        st.write(context.content)
        else:
            st.write("The end")



