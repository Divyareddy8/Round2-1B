# Use official full Python image with AMD64 architecture (no GPU)
FROM --platform=linux/amd64 python:3.11

# Set working directory inside the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    python3-dev \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files including requirements.txt
COPY . .

# Install Python dependencies (CPU-only Torch version)
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download required NLTK corpora
RUN python -m nltk.downloader punkt stopwords

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Run model download script (if required)
RUN python src/download_models.py

# Run the app
CMD ["python", "src/main.py"]