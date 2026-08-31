# ── Stage 1: build ───────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libgdk-pixbuf-2.0-0 libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev libxml2 libxslt1.1 \
    shared-mime-info fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN DJANGO_SETTINGS_MODULE=ev_project.settings \
    DJANGO_SECRET_KEY=build-time-key \
    python manage.py collectstatic --noinput

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libgdk-pixbuf-2.0-0 libgdk-pixbuf-xlib-2.0-0 \
    libxml2 libxslt1.1 \
    shared-mime-info fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /app /app

# Create runtime directories and non-root user
RUN mkdir -p /tmp/django_sessions /app/media/csv_cache && \
    groupadd -r evapp && useradd -r -g evapp evapp && \
    chown -R evapp:evapp /app /tmp/django_sessions

USER evapp

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=ev_project.settings

EXPOSE 8000

CMD ["gunicorn", "ev_project.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-"]
