FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Set default Gunicorn settings with reduced workers to save memory
ENV GUNICORN_WORKERS=1
ENV GUNICORN_TIMEOUT=120
ENV PORT=8000

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Start the application using Gunicorn with migrations and seeding admin before
CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_admin && gunicorn --workers $GUNICORN_WORKERS --timeout $GUNICORN_TIMEOUT --bind 0.0.0.0:$PORT config.wsgi:application"]
