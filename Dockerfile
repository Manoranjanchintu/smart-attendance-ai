# Use a Miniconda base image to get pre-built AI binaries
FROM continuumio/miniconda3:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Step 1: Install dlib and Python 3.11 using Conda
# We use the 'classic' solver to avoid plugin/lock issues on Render
RUN conda clean --all -y && \
    conda install --solver=classic -c conda-forge dlib=19.24.1 python=3.11 -y

# Step 2: Install other requirements via pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
