# Use a Miniconda base image to get pre-built AI binaries
FROM continuumio/miniconda3:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Step 1: Install dlib using Conda (This downloads a PRE-BUILT binary)
# No compilation = No memory crash!
RUN conda install -c conda-forge dlib=19.24.1 -y

# Step 2: Install other requirements via pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 5000

# Command to run the application
# We use the full path to the conda environment's gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
