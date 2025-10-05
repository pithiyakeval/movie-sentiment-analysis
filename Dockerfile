FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY flask-app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create NLTK data directory and download data
RUN mkdir -p /usr/local/nltk_data
RUN python -c "import nltk; nltk.download('vader_lexicon', download_dir='/usr/local/nltk_data')"
RUN python -c "import nltk; nltk.download('punkt', download_dir='/usr/local/nltk_data')"

# Force extract the zip files
RUN cd /usr/local/nltk_data/sentiment && unzip -o vader_lexicon.zip
RUN cd /usr/local/nltk_data/tokenizers && unzip -o punkt.zip

# Verify the extraction worked
RUN ls -la /usr/local/nltk_data/sentiment/ && ls -la /usr/local/nltk_data/tokenizers/

# Copy application
COPY flask-app/ .

# Set environment variables
ENV NLTK_DATA=/usr/local/nltk_data
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "app.py"]