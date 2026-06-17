FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download essentia TF models (host can be flaky; build fails loudly if unavailable)
RUN mkdir -p /app/models && cd /app/models && \
    base=https://essentia.upf.edu/models && \
    wget -q $base/feature-extractors/discogs-effnet/discogs-effnet-bs64-1.pb && \
    wget -q $base/classification-heads/mood_happy/mood_happy-discogs-effnet-1.pb && \
    wget -q $base/classification-heads/mood_sad/mood_sad-discogs-effnet-1.pb && \
    wget -q $base/classification-heads/mood_relaxed/mood_relaxed-discogs-effnet-1.pb && \
    wget -q $base/classification-heads/mood_aggressive/mood_aggressive-discogs-effnet-1.pb && \
    wget -q $base/classification-heads/mood_party/mood_party-discogs-effnet-1.pb && \
    wget -q $base/classification-heads/danceability/danceability-discogs-effnet-1.pb

COPY *.py ./

RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1 MODELS_DIR=/app/models
EXPOSE 8000
CMD ["python", "service.py"]
