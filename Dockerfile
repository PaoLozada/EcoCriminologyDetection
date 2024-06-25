ARG PORT=443

# Use a slim Python base image
FROM python:3.11-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    cmake \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .


# Command to run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
