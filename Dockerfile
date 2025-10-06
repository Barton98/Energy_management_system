# Simple Dockerfile for EMS API demonstration
# Mid-level Docker usage - straightforward and functional

FROM python:3.13-slim

# Set environment variables  
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port that the app runs on
EXPOSE 8000

# Run the application
CMD ["python", "api.py"]

# This Dockerfile demonstrates:
# - Basic containerization concepts
# - Proper dependency management
# - Clean, readable Docker practices
# - Suitable for development and demo purposes