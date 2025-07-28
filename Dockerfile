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

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies (CPU-only Torch version)
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download required NLTK corpora
RUN python -m nltk.downloader punkt stopwords

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Download HuggingFace models
COPY src/download_models.py ./src/
RUN python src/download_models.py

# Now copy the rest of the project (source code, etc.)
COPY . .

# Run the app
CMD ["python", "src/main.py"]
