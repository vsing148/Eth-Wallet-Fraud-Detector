# Use a slim Python image to save space
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy your requirements
COPY requirements.txt .

# Install dependencies (We use the CPU-only version of PyTorch to save MASSIVE space)
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Copy all your backend files into the container
COPY . .

# Expose the port FastAPI uses
EXPOSE 8000

# Command to run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]