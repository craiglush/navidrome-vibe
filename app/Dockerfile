FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY vibe/ ./vibe/
COPY server.py .
COPY templates/ ./templates/
COPY static/ ./static/

ENV PYTHONUNBUFFERED=1
EXPOSE 4546
CMD ["gunicorn", "--bind", "0.0.0.0:4546", "--workers", "2", "--timeout", "180", "server:create_app()"]
