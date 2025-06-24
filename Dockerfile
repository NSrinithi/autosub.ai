FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install system dependencies
RUN apt-get update && xargs -a apt.txt apt-get install -y && apt-get clean

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Run app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
