FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install system packages directly
RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose correct port
ENV PORT=10000

# Start the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]

