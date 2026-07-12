# Use official Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies (git is required for PocketFlow)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone PocketFlow dependency to a standard container path and set environment variable
RUN git clone https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge.git /pocketflow
ENV POCKETFLOW_PATH=/pocketflow

# Copy the rest of the application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Configure Streamlit to run headlessly and listen on all interfaces
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the application
ENTRYPOINT ["streamlit", "run", "app.py"]
