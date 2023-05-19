FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR ./backend

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files to the container
COPY . .

CMD alembic revision --autogenerate; alembic upgrade heads; gunicorn app:create_app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000