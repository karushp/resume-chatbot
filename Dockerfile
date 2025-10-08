FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY backend/ .

# Expose port (Fly.io will set PORT environment variable)
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
