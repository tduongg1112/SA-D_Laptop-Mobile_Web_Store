FROM python:3.10-slim

WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port
EXPOSE 80

# Command to run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
