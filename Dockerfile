# Use official full Python image with AMD64 architecture (no GPU)
FROM --platform=linux/amd64 python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    python3-dev \
    git \
    curl \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies (CPU-only Torch version)
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Download required NLTK corpora
RUN python -m nltk.downloader punkt_tab punkt stopwords

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Download HuggingFace models
RUN python src/download_models.py

# Default command to run the app
CMD ["python", "src/main.py"]