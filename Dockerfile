# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app


#Copying files with dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/


# Copy other files
COPY . .

# Create a simple logo.png if it doesn't exist
RUN if [ ! -f logo.png ]; then \
    echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" | base64 -d > logo.png; \
fi

# Expose ports
EXPOSE 3000 
EXPOSE 5001

# Run the application
CMD ["python", "main.py"]
