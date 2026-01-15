# AiStagePlayGen

An AI-powered stage play generator that uses LLMs to collaboratively write theatrical scripts. The system uses a LangGraph-based agentic workflow to generate multi-chapter stage plays with character development, dynamic narrative progression, and human-in-the-loop capabilities.

## Features

- Generate theatrical scripts with multiple chapters and acts
- Dynamic character creation with relationship tracking
- Human-in-the-loop interrupts for creative guidance
- Checkpoint persistence for resuming interrupted stories
- Web UI via Streamlit

## Prerequisites

- Python 3.11+
- OpenAI API key

## Local Development

### 1. Clone and setup

```bash
git clone <repository-url>
cd AiStagePlayGen
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Initialize the database (optional)

The database tables are created automatically on first run. To seed with example characters:

```bash
python db/init_stagestate.py
```

### 4. Run the application

**Streamlit UI (recommended):**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**FastAPI server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker

### Build the image

```bash
docker build -t aistageplaygen .
```

### Run locally with Docker

```bash
docker run -p 8080:8080 -e OPENAI_API_KEY=your-key-here aistageplaygen
```

Then open http://localhost:8080 in your browser.

## Project Structure

```
AiStagePlayGen/
├── app.py                 # Streamlit web UI (main entry point)
├── main.py                # FastAPI REST server (alternative)
├── agent_graph.py         # LangGraph workflow and state machine
├── config.py              # Configuration and secrets management
├── agent_tools/           # LLM tools
│   ├── characters.py      # Character creation tool
│   └── human_in_the_loop.py  # Human assistance interrupt
├── db/                    # Database layer
│   ├── handler.py         # SQLAlchemy ORM and CRUD operations
│   └── init_stagestate.py # Seed data script
├── prompts/               # System prompts
│   └── playwriter_prompts.py
├── .streamlit/            # Streamlit configuration
│   └── config.toml
├── Dockerfile             # Container configuration
└── requirements.txt       # Python dependencies
```

## How It Works

1. **User Input**: Enter a story prompt to begin
2. **Agent Loop**: The LangGraph agent writes lines of dialogue/narration
3. **Chapter Progression**: After reaching the chapter length, a synopsis is generated and a new chapter begins
4. **Character Creation**: The agent can create new characters mid-story using the `create_character` tool
5. **Human Assistance**: The agent can request human input via the `human_assistance` tool
6. **Story Completion**: After all chapters, an ending is generated

## Configuration

The `StagePlayWriter` class accepts these parameters:

- `themes`: Thematic elements for the story
- `vibe`: Tone and style guidance
- `setting`: Story location/world
- `number_of_chapters`: Total chapters to generate

## License

MIT
