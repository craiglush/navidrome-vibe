FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY vibe/ ./vibe/
COPY server.py .
COPY templates/ ./templates/
COPY static/ ./static/

RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1
EXPOSE 4546
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:4546/healthz').status==200 else 1)"
CMD ["gunicorn", "--bind", "0.0.0.0:4546", "--workers", "2", "--timeout", "180", "server:create_app()"]
