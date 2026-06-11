# Lightweight Python base image
FROM python:3.12-slim

# Working directory
WORKDIR /app

# Install dependencies first (Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Container exposed port
EXPOSE 8000

# Startup command
CMD ["python", "app.py"]
