# Dockerfile
FROM python:3.11-slim

# Avoid .pyc and have unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies: build tools + node for Tailwind
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 1) Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 2) Install Node dependencies for Tailwind
COPY package.json package-lock.json* ./
RUN npm install

# 3) Copy the rest of the project
COPY . .

# 4) Build Tailwind CSS (uses the script you defined in package.json)
RUN npm run tailwind:build

# 🔑 NEW: run database migrations (SQLite) at build time
RUN python manage.py migrate --noinput

# 5) Collect static files into STATIC_ROOT (staticfiles/)
RUN python manage.py collectstatic --noinput

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Default environment; you override in production with DJANGO_DEBUG=0
ENV DJANGO_DEBUG=0

# Launch the app with Gunicorn
CMD ["sh", "-c", "gunicorn LITRevu.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
