# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY config/ config/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV INVOICE_SORTER_CONFIG=/app/config/settings.yaml

# Create entrypoint script
RUN echo '#!/bin/bash\npython -m src.core.processor' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Run the processor
ENTRYPOINT ["/app/entrypoint.sh"]
