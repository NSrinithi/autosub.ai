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

# 🔧 Create upload/output folders
RUN mkdir -p /app/uploads /app/subtitles && chmod -R 777 /app/uploads /app/subtitles

# Expose correct port (optional)
# ENV PORT=10000  ← you can remove this if using $PORT from Render

# Start the app with dynamic port from Render
CMD gunicorn app:app --bind 0.0.0.0:$PORT
