from langchain_core.messages import HumanMessage
from agent_graph import StagePlayState
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent_graph import StagePlayWriter


def print_stream(stream):
    for s in stream:
        message = s["context"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


if __name__ == "__main__":
    load_dotenv()
    llm = ChatOpenAI(model="gpt-4o-mini")
    # tools = [get_character_description, create_character, human_assistance]

    inputs = StagePlayState(
        counter=0,
        context=[
            HumanMessage(
                """Narrator: It is a sunny wistful day in Tam Tamouree,
            Swedenborg and Luna lazily scout over the townspeople from their hidden vantage point atop the old church.
            Luna:
            """
            )
        ],
    )

    graph_config: RunnableConfig = RunnableConfig({"configurable": {"thread_id": "new_thread_id"}})

    playwriter = StagePlayWriter(
        llm=llm,
        themes= """Loss of innocence, Becoming Psychologically whole, Jungian Psychology, Bildung""",
        vibe= """Subtly, Weird and funky""",
        setting= "Tam Tamoree, fictional town in German Bavaria",
        number_of_chapters= 4
    )

    print_stream(playwriter.graph.stream(input=inputs,stream_mode="values" ,config= graph_config))
