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

# Expose the port Gunicorn will run on
EXPOSE 5000

# Command to run the application using Gunicorn
# 'wsgi:app' refers to the 'app' object in the 'wsgi.py' file
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]