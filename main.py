from fastapi import FastAPI
from agent_graph import StagePlayWriter, StagePlayState
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from config import get_openai_api_key

# Initialize OpenAI API key from config (handles both local and cloud)
get_openai_api_key()
app = FastAPI()
llm = ChatOpenAI(model="gpt-5-mini")

inputs = StagePlayState(
    line=0,
    chapter=1,
    context=[
        HumanMessage(
            """Narrator: It is a sunny wistful day in Tam Tamouree,
        Swedenborg and Luna lazily scout over the townspeople from their hidden vantage point atop the old church.
        Luna:
        """
        )
    ],
)

playwriter = StagePlayWriter(
    llm=llm,
    themes= """Loss of innocence, Becoming Psychologically whole, Jungian Psychology, Bildung""",
    vibe= """Subtly, Weird and funky""",
    setting= "Tam Tamoree, fictional town in German Bavaria",
    number_of_chapters= 4
)
thread_id = "just_a_thread"
connection_string_checkpointer = "db/graph_checkpoints/checkpoints.db"


@app.get("/start")
async def start_graph() -> dict[str, str]:
    """Start the agent application
    """
    # thread_id = uuid4
    config = RunnableConfig({"configurable": {"thread_id": thread_id}})
    async with AsyncSqliteSaver.from_conn_string(connection_string_checkpointer) as checkpointer:
        async for event in (playwriter
                            .build_graph(checkpointer)
                            .astream(input=inputs, config= config, stream_mode="values")):

            message = event["context"][-1]
            if isinstance(message, tuple):
                print(event)
            else:
                message.pretty_print()

    return {"status": "Graph started, may be paused"}


@app.get("/resume")
async def resume_graph(input: str):
    config = RunnableConfig({"configurable": {"thread_id": thread_id}})
    resume_input = Command(resume= {"data": input})
    
    async with AsyncSqliteSaver.from_conn_string(connection_string_checkpointer) as checkpointer:
        async for event in (playwriter
                            .build_graph(checkpointer)
                            .astream(input=resume_input, config= config, stream_mode="values")):

            message = event["context"][-1]
            if isinstance(message, tuple):
                print(event)
            else:
                message.pretty_print()
    return {"status": "Resumed"}


@app.get("/test_api")
async def test()-> dict[str,str]:
    return {"status" :"all good"}

# Run: uvicorn main:app --host 0.0.0.0 --port 8000