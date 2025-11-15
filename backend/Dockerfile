# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose the port Gunicorn will run on
EXPOSE 5000

# Command to run migrations then start gunicorn
CMD ["/app/start.sh"]
