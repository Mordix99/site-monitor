FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the  requirements.txt file to the container at /app
COPY requirements.txt .
# intall dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code to the container
COPY main.py ./
# Set the command to run the application
CMD ["python","-u", "main.py"]

