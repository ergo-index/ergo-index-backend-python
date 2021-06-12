# Use Docker image with Python version 3.
FROM python:3.7.4

# Print messages immediately instead of using a buffer.
ENV PYTHONUNBUFFERED 1

# Install dependencies or use Docker cache.
ADD project_settings.env backend/project_settings.env
ADD backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy Python code into Docker.
ADD backend backend
ADD backend/ergo_index_fund_api ergo_index_fund_api
ADD backend/manage.py /manage.py
RUN mkdir /sessions

# Populate the sql database with django models and settings.
CMD ["python", "manage.py", "migrate", "auth"]
CMD ["python", "manage.py", "createadminuser"]
# Detect any django changes that need to alter the sql database structure.
CMD ["python", "manage.py", "makemigrations"]
# Apply migrations to update the sql database schema.
CMD ["python", "manage.py", "migrate", "--fake-initial"]
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "createadminuser"]

# Start the application server (gunicorn).
CMD ["gunicorn", "--bind", "0.0.0.0:8082", "ergo_index_fund_api.wsgi:application", "--timeout", "90"]