FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for WeasyPrint and PDF generation
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -e .

# Copy application code
COPY app app/
COPY scripts scripts/

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Create storage directory
RUN mkdir -p /app/storage/resumes

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
