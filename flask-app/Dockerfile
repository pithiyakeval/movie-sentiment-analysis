FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN mkdir -p /usr/local/nltk_data
RUN python -m nltk.downloader vader_lexicon -d /usr/local/nltk_data
RUN python -m nltk.downloader punkt -d /usr/local/nltk_data

# Copy application code
COPY . .

# Environment
ENV NLTK_DATA=/usr/local/nltk_data
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "app.py"]
