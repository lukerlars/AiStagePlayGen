import streamlit as st

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from agent_graph import StagePlayWriter, input_message
from langgraph.types import Command, Interrupt
from langgraph.checkpoint.sqlite import SqliteSaver
from uuid import uuid4
from config import get_openai_api_key

# Initialize OpenAI API key from config (handles both local and cloud)
get_openai_api_key()
llm = ChatOpenAI(model="gpt-4o-mini")

conn_checkptr = "db/graph_checkpoints/checkpoints.db"

# Initialize session state for persistence across Streamlit reruns
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interrupted" not in st.session_state:
    st.session_state.interrupted = False
if "interrupt_query" not in st.session_state:
    st.session_state.interrupt_query = None
if "story_started" not in st.session_state:
    st.session_state.story_started = False

thread_id = st.session_state.thread_id
graph_config: RunnableConfig = RunnableConfig({"configurable": {"thread_id": thread_id}})

playwriter = StagePlayWriter(
    llm=llm,
    themes="Loss of innocence, Becoming Psychologically whole, Jungian Psychology, Bildung",
    vibe="Subtly, Weird and funky",
    setting="Tam Tamoree, fictional town in German Bavaria",
    number_of_chapters=4
)

# Title
st.title("Playwriter")

# Display previous messages
for msg in st.session_state.messages:
    st.write(msg)


def run_graph(graph, input_data, config):
    """Run the graph and handle events, checking for interrupts."""
    for event in graph.stream(input=input_data, config=config, stream_mode="values"):
        context = event.get("context", [])
        if context:
            last_message = context[-1]
            content = getattr(last_message, 'content', str(last_message))
            if content and content not in st.session_state.messages:
                st.session_state.messages.append(content)
                st.write(content)

    # Check for interrupt after streaming completes
    state = graph.get_state(config)
    if state.next:  # Graph is paused (has next nodes to execute)
        # Check if there's an interrupt in the state
        if hasattr(state, 'tasks') and state.tasks:
            for task in state.tasks:
                if hasattr(task, 'interrupts') and task.interrupts:
                    for interrupt in task.interrupts:
                        return True, getattr(interrupt, 'value', str(interrupt))
    return False, None


# Handle interrupt state - show input for human assistance
if st.session_state.interrupted:
    st.warning(f"Agent needs help: {st.session_state.interrupt_query}")
    human_input = st.text_input("Your response:", key="human_response")

    if st.button("Submit Response"):
        if human_input:
            with SqliteSaver.from_conn_string(conn_checkptr) as checkpointer:
                graph = playwriter.build_graph(checkpointer)
                resume_command = Command(resume=human_input)

                st.session_state.interrupted = False
                st.session_state.interrupt_query = None

                interrupted, query = run_graph(graph, resume_command, graph_config)

                if interrupted:
                    st.session_state.interrupted = True
                    st.session_state.interrupt_query = query
                    st.rerun()
                else:
                    st.success("Story complete!")

# Main input for starting the story
elif not st.session_state.story_started:
    user_input = st.text_input("Enter your story prompt:")

    if st.button("Start"):
        if user_input:
            st.session_state.story_started = True
            st.session_state.messages = []  # Clear previous messages

            with SqliteSaver.from_conn_string(conn_checkptr) as checkpointer:
                graph = playwriter.build_graph(checkpointer)

                interrupted, query = run_graph(graph, input_message(user_input), graph_config)

                if interrupted:
                    st.session_state.interrupted = True
                    st.session_state.interrupt_query = query
                    st.rerun()
                else:
                    st.success("Story complete!")
else:
    # Story is running but not interrupted - show completion or allow restart
    st.info("Story generation complete.")
    if st.button("Start New Story"):
        st.session_state.thread_id = str(uuid4())
        st.session_state.messages = []
        st.session_state.interrupted = False
        st.session_state.interrupt_query = None
        st.session_state.story_started = False
        st.rerun()
