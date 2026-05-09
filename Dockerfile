# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Step 1: Install numpy first (required for many AI builds)
RUN pip install --no-cache-dir numpy==1.26.4

# Step 2: Install dlib using a pre-built binary wheel to AVOID the 8GB memory crash
# This wheel is for Python 3.11 on 64-bit Linux (which Render uses)
RUN wget https://github.com/jloh02/dlib-wheels/releases/download/v19.24.2/dlib-19.24.2-cp311-cp311-linux_x86_64.whl && \
    pip install dlib-19.24.2-cp311-cp311-linux_x86_64.whl && \
    rm dlib-19.24.2-cp311-cp311-linux_x86_64.whl

# Step 3: Install the rest of the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
