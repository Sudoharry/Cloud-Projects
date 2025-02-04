# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies, including Graphviz
RUN apt-get update && apt-get install -y graphviz libgraphviz-dev

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first for better Docker layer caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip &&  pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
