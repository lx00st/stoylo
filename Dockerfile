FROM python:3.12

# Install OpenCV system dependencies
RUN echo "force rebuild 1" && apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglx0 \
    libgl1-mesa-dri \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Command to run your application (e.g., uvicorn, python main.py)
CMD ["python", "main.py"]