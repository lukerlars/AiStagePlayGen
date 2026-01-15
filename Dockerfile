FROM python:3.12-slim

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directories
RUN mkdir -p db/graph_checkpoints db/stageplay

# Initialize the database schema (creates tables if they don't exist)
RUN python -c "from db.handler import Base, engine; Base.metadata.create_all(engine)"

# Expose port for Cloud Run
EXPOSE 8080

# Run Streamlit with production settings
CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--browser.gatherUsageStats=false", \
     "--server.headless=true"]
