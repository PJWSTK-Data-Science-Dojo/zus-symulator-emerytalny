FROM python:3.12.3-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY app .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI default port
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
